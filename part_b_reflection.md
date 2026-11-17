Module 3



Part A tekninen kokonaisuus

Ensimmäisessä osiossa rakensin pienen hybridi reaktiivis-deliberatiivisen
ohjausjärjestelmän. Reaktiivinen kerros vastaa LiDAR:in havaitsemasta
esteistä, joita tulee robotin eteen. Deliberatiivinen paikallistason toimino jatkaa kulkua eteenpäin, kun havaitsee reitin olevan esteetön. Oheessa kaavio hahmottamassa kokonaisuuden toimintaa.


Webots LDS-01 LiDAR
				│
				▼
			/scan ──► IsObstacleTooClose
										 │
						 Behavior Tree 10 Hz
								 ┌───┴────┐
						 este havaittu  vapaa reitti
								 │              │
							TurnAway      DriveForward
								 └──────┬───────┘
												▼
										 /cmd_vel
												│
												▼
								 Webots RobotDriver
												│
												▼
										pyörät
```

ROS aiheiden tyypit ovat /scan = sensor_msgs/LaserScan sekä /cmd_vel =
geometry_msgs/TwistStamped. Webots ajuri julkaisee lisäksi /odom
liikkeen todentamiseen.

Task 1 Lehtikäyttäytymiset

Tiedosto hybrid_assignment/task1_behaviours.py

Käytetyt Säätöarvot

   python
OBSTACLE_THRESHOLD = 0.5
FORWARD_ARC_DEG = 30
DRIVE_SPEED = 0.3
TURN_SPEED = 0.8
TURN_SCAN_ANGLE_DEG = 60.0


- OBSTACLE_THRESHOLD määrää, koska mittaus lasketaan liian lähellä olevaksi esteeksi.
- FORWARD_ARC_DEG taas määrittää suoraan eteenpäin katsovan tarkistusalueen puoliavauskulman.
- DRIVE_SPEED sekä TURN_SPEED määräävät eteenpäin- sekä kääntönopeuden.
- TURN_SCAN_ANGLE_DEG taas on lisätyn väistöpuolen sektorin keskus.

1 a IsObstacleTooClose

Kyseessä on Condition käyttäytyminen. Tämän tehtävänä on palauttaa SUCCESS jos
LiDAR:in etusektorissa havaitaan alle 0,5 metrin säteellä oleva este. Muutoin taas lopputuloksena on FAILURE.

- Konstruktori tilaa /scan aiheen sekä asettaa latest_scan arvoksi aluksi None tilnteen alkuvaiheessa.
- _scan_callback taas tallentaa uusimman LaserScan viestin.
- update palauttaa FAILURE, jos skannausta ei ole vielä saatu. Näin
	ensimmäisen puun tikki ei pääse kaatumaan.
- Jokainen säteen kulma lasketaan angle_min + index * angle_increment tyylisellä
	kaavalla, mikä kierretään välille −π…π atan2(sin(angle), cos(angle))
	laskutavalla. Indeksiä 0 ei tulkita eteenpäin osoittavaksi.
- Vain ± FORWARD_ARC_DEG alueen mittaukset tarkastetaan.
- inf, NaN, nolla SEKÄ negatiiviset etäisyydet ohitetaan. Estehavainto syntyy
	vain hYVÄKSYTYSTÄ etäisyydestä, joka on aidosti alle kynnyksen.
- Tätysin sektorin rajalla olevassa testissä liukulukujen pyöristys
	aiheutti ensin mittauksen ohittumisen. Rajavertailuun lisättiin
	math.isclose, jonka jälkeen rajatesti alkoi mennä läpi.

1 b TurnAway

TurnAway on Action käyttäytymistä. Tämä julkaisee aikaleimatun
TwistStamped viestin /cmd_vel aiheeseen pitämällä lineaarisen nopeuden
nollassa palauttaen RUNNING. Toimintona on päätös siitä, milloin
kääntyminen keskeytetään.

Toteutuksessani robotin toiminnot hyödyntävät uusimman /scan viestiä.
initialise suoritetaan väistöjakson alussa, jossa verrataan vasenta sekä oikeaa
etuviistosektoria. Molemmat sektorit ovat keskitetty ±60 asteeseen, jonka
puoliavaus on FORWARD_ARC_DEG. Sektorin lähin kelvollinen mittaus kuvaa
kyseisen hetken vapautta. Tällöin robotti valitsee puolen, jossa lähin este on
etäämpänä pitämällä valinnan samana kyseisen väistöjakson aikana. Jos skannausta
ei tapahdu niin tällöin oletussuunta on vasen.

TODO 1 b

Tässä osiossa määritellään angular.z = TURN_SPEED, eli kääntyminen vasemmalle. Homasin kuitenkin robotin aina välillä jumiutuvan pelkällä yhden suunnan kääntymisellä, joten toteutuksessani voi lähettää myös -TURN_SPEED silloin kun oikea puoli on vapaampi. Tämä on tehtävänannon
vasemmalle kääntyvän perusratkaisun päälle lisätty väistöparannus. Validoin tämän molempien
kääntymissuuntien testeillä sekä Webots controllerin synteettisillä LiDAR skannauksilla.

DriveForward

Tehtävänannossa valmiiksi annettu jatkuva Action käyttäytyminen.
Jokaisella päivityksellä tämä julkaisee /cmd_vel aiheeseen nykyhetken
aikaleiman, linear.x = DRIVE_SPEED sekä angular.z = 0.0 palauttamalla
RUNNING. Tämä ei suorita päättymisehtoa itse vaan reaktiivinen haara auorittaa keskeytyksen kun esteitä havaitaan.

Task 2 Behavior Treen kehittäminen

Tiedosto hybrid_assignment/task2_tree.py

PatrolTreeNode luo kolme lehtikäyttäytymistä rakentamalla ohjeistuksen mukaisen prioriteettipuun.

   text
Root: Selector(memory=False)
├── Reactive: Sequence(memory=False)
│   ├── IsObstacleTooClose
│   └── TurnAway
└── Deliberative: Sequence(memory=False)
		└── DriveForward


- Reactive haarassa este-ehto on ennen kääntymistoimintoa.
- Selector tarkistaa reaktiivisen haaran ennen deliberatiivista jokaisen tikin osalta.
- Kun ehto palauttaa SUCCESS niin väistötoiminto palauttaa RUNNING. Tällöin
  eteenpäinajon haaraa ei tikata.
- Kun ehto palauttaa FAILURE niin Selector siirtyy DriveForward haaraan.
- memory=False taas pitää este-ehdon tarkistettavana myös kun toiminto
  on edellisellä tikillä RUNNING tilassa.
- Puu alustetaan BehaviourTree.setup(timeout=15) komennolla. ROS ajastin
  tikkaa puuta 10 Hz:n taajuudella.
- _tick kutsuu self.tree.tick() tulostaen
  py_trees.display.unicode_tree(..., show_status=True) terminaaliin. Käynnistyessä
  puun rakenne tulostuu ilman tiloja.
- Puun haaravalinta tulee Selectorin sekä Sequencejen rakenteesta. Kokoamisessa
  ei käytetä erillistä if/else ohjausta.

Webots- sekä ROS 2 integraatio

tiedostot

- launch/assignment.launch.py käynnistää WebotsController sekä
  task2_tree ROS solmun.
- resource/TurtleBot3Burger.urdf kytkee LDS-01-LiDAR:in /scan aiheeseen
	liittämällä Webots-ajurin robottiin.
- hybrid_assignment/robot_driver.py muuntaa /cmd_vel viestin
	differentiaalipyörien nopeuksiksi julkaisemalla pyöräantureista lasketun
	/odom  odometrian.
- worlds/break_room.wbt on käytetty Webots maailma. Koodin tähän löysin tehtävänannon ohjeistuksesta, jonka kopioion vscodessa määritettyyn sijaintiin.
- package.xml, setup.py sekä setup.cfg määrittävät ament Python-paketin,
	ROS-riippuvuudet, asennettavat resurssit sekä `task2_tree`-komennon.

Testit sekä tulokset

Komento, jolla paketti rakennettiin sekä ajettiin kaikki testit


cd /ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select hybrid_assignment
source install/setup.bash
python3 -m pytest -q src/hybrid_assignment/test


Viimeisessä ajossa build onnistui, jolloin kaikki 18 testiä
läpäisivät 14 Task 1 testiä sekä 4 Task 2 testiä.

Webots/ROS 2 -launch

ros2 launch hybrid_assignment assignment.launch.py


Tarkistuksissa WebotsController yhdistyi TurtleBot3 Burgeriin. /scan mittauksia saatiin, /cmd_vel komennot toimivat sekä /odom vahvisti robotin liikkumista. Synteettisellä eteen sekä vasemmalle sijoitetulla testiskannauksella puu julkaisi oikealle kääntävän komennon
linear.x = 0, angular.z = -0.8. peilikuvana oikealla oleva este
tuotti vasemmalle kääntävän komennon angular.z = +0.8. /odom vahvisti
Webots-simulaatiossa noin −0,546 rad suuntamuutoksen. Skannauksen
vapauttamisen jälkeen testasin myös eteenpäinajon toimintaa.

LiDAR on vaakatasossa toimiva yksitasoinen sensori. Jos matala hylly jää skannaustason alapuolelle eikä näinollen tuota /scan mittausta, tätä hyllyä ei voida havaita nykyisellä sensorilla tai pelkällä este-ehdon koodilla. Totesin tämän webotsissa, jossa laitoin skannausalueen toiminnin käyttöön. Tehtävän toteutus käyttää kuitenkin kaikkia etusektorissa LiDAR:in ilmoittamia
kelvollisia mittauksia. Näin ollen en halunnut riskeerata toimivaa kokonaisuutta yhden osion selvittämisen takia.

Part B Oppiminen sekä työskentely

Seuraavat vastaukset ovat Part B arviointiosiota.

1. Mitä opin?

Opin vahvasti sen, että sensoritaulukon indeksi ei itsessään kerro missä suunnassa este on.
Tämä pitää laskea LiDAR viestin angle_min sekä angle_increment arvoista.
Ymmärsin uudella tasolla sen miksi inf pitää ohittaa sekä miksi ensimmäinen
latest_scan is None tilanne pitää käsitellä ennen mittausten läpikäyntiä.

Behavior Tree puussa status on osa ohjauslogiikkaa. Este-ehto ei yksissään pysäytä
tai käännä robottia. Tämän SUCCESS saa Selectorin valitsemaan reaktiivisen
haaran. Esteen poistuessa ehto palauttaa FAILURE, jonka jälkeen Selector
siirtyy eteenpäinajoon. Reaktiivisen haaran prioriteetti on näin ollen ilmaistu
puun rakenteessa.

Lisäksi opin seuraamaan ROS 2 aiheiden rajapintaa Webotsin sekä käyttäytymisten
välillä. /scan, /cmd_vel sekä /odom auttoivat erottamaan sen julkaiseeko
ohjelma komennon ja liikkuuko simuloitu robotti oletetulla tavalla.

2. Miten ratkaisin ongelmia ja mitä työkaluja käytin tähän?

Etenin hallituissa vaiheissa kunnes kokonaisuus oli ratkaistu. Ensin aloitin DriveForward, jonka jälkeen LiDAR ehtoon sekä TurnAway osioon. Tämän jälkeen puun prioriteettirakenteseen ja lopuksi Webots/ROS 2 integraatioon. Käytin tehtävänannossa ollutta README osiota, py_trees ohjeita,
Pylancen diagnostisia tietoja, terminaalia tehtyjä komentoja varten, colcon buildia, pytest-testejä
sekä Webots ROS aiheita sekä odometriaa.

Tekoälynä käytin vscoden omaa copilot agent Luna-6 mallia ilmaisversiona. Hyödynsin tätä tarvittaessa toteutus- sekä vianrajauskohdissa. Apuri auttoi ideoinnissa testien luonnostelussa, kuten LiDAR-kulmien käsittelyssä sekä Behavior Treen rakentamisessa.
Tein tätä haastavimmissa osioissa maltillisesti aina tarkastamalla sekä testaamalla apurin antamat ideat oikeasti toimiviksi vaihtoehdoiksi, joilla pystyy tuottamaan toimivan tehtävänannon mukaisen kokonaisuuden.


3. Työkalujen sekä ongelmanratkaisun arviointi

Hyvänä esimerkkinä on väistösuunnan valinta. Tehtäväpohjassa pyydetään
TurnAway toimintoa pyörimään vasemmalle. Testasin tätä Webots maailmassa. Totesin tämän jälkeen, että vasemmalla oleva este voi tehdä pelkän vasempaan kääntymisen vaillinaiseksi toiminnoksi vertasin näinollen vasenta sekä oikeaa LiDAR sektoria.
Varmistin muutoksen peilikuvaisilla testeillä sekä Webots controlleriin
kytketyillä /cmd_vel sekä /odom mittauksilla.

Mielestäni tämä ratkaisu on toiminnon kannalta hyödyllinen. Tämä muuttaa hieman
tehtävänannossa ollutta aina vasemmalle kääntyvää toimintoa, joka mainittiin TODO 1b osiossa. Laajentamalla kääntymisen molempiin puoliin niin huomasin rtobotin liikkuvan paremmin webots maailmassa. Ainoastaan matala hylly lopetti tämän liikkumisen, mutta muuten pystyi väistämään esteet ilman ongelmia.

Samalla toinen konkreettinen virhe löytyi testistä itsestään. Tasan sektorin rajalla
olevan säteen kulma jäi liukulukupyöristyksen takia aluksi määritetyn rajan ulkopuolelle.
Testin epäonnistuessa selvitin ongelman, jonka jälkeen rajavertailuun lisättiin
math.isclose. Korjauksen jälkeen rajatesti sekä testisarja menivät läpi.

Mainitsemani matalan hyllyn näkyvyyttä arvioitiin Webotsin LiDAR pistepilven avulla.
Tämä jäi vaakatasoisen skannauskentän alapuolelle. Tämä kokemus opetti minua erottamaan
ohjelmistovirheen sensorin fyysisestä näkökentästä. Tämä tarkoittaa, että este-ehto ei voi
reagoida mittaukseen, jota /scan itsessään ei sisällä.

4. Oma oppiminen sekä työskentelyprosessit

Kokonaisuudessaan haastavinta oli yhdistää sensorin geometria, pyörännopeuskomennot sekä
Behavior Treen tilat yhdeksi selkeäksi toimivaksi kokonaisuudeksi. Pienet
toistettavat testit, joiden jälkeen tehty Webots-koe toimivat omalta osalta paremmin kuin
pelkkä koodin tulkinta. Erityisen hyödyllistä oli varmistaa /cmd_vel komennot sekä /odom liike.

Ymmärrän ksiken tämän jälkeen paremmin, että toimiva koodi ei yksissään todista sensorin havaitsevan jokaista ympäristössä olevaa estettä. Tätä varten tarkistin LiDAR:in pistepilven, kokeilin estehavaintoa, seurasin puun tulostetta sekä vertasin näitä robotin liikkumiseen.
Tälleen erotin anturin näkökentän rajoituksen käyttäytymiskoodin ongelmasta.

Jos tekisin vastaavan tehtävän uudelleen niin varmistaisin alkuvaiheessa Webots
controller yhteyden, LiDAR:in suunnat sekä sensorin korkeuden. Tällöin eteentullutta hyllykorkeuden ongelmaa ei välttämättä tulisi saatuun loputulokseen kaiken tekemisen jälkeen. Kirjaisin myös saaduttestitulokset vaiheittain sekä erottaisin alusta asti tehtävänannon antamat
vaatimukset omista sovelluksista toimivampaan lopputulokseen.

Myös tehtyjen Testien löytämät rajatapaukset sekä Webotsin havainnot antoivat osviittaa sekä ideoita siihen, että mitä tulisi korjata ja miten. Opin parhaiten kokonaisuuden toimivuuden
juurikin näissä kohdissa, joissa jouduin selittämään, miksi tila, mittaus tai
komento osiot muuttuivat. Kaikkiin näihin löytyi lopulta toimiva ratkaisu haluttua lopputulosta varten.


Tiedostokohtainen koodikatsaus


hybrid_assignment/task1_behaviours.py

Tässä osiossa ovat Behavior Treen kolme lehtikäyttäytymistä sekä niitä
ohjaavat säätöarvot.

Importit sekä vakiot


OBSTACLE_THRESHOLD = 0.5
FORWARD_ARC_DEG = 30
DRIVE_SPEED = 0.3
TURN_SPEED = 0.8
TURN_SCAN_ANGLE_DEG = 60.0


Vakiot pitävät este-etäisyyden, tarkastelukulman sekä nopeudet yhdessä
paikassa. Viimeinen kulmavakio liittyy toteutuksen lisäykseen, jossa
käännöksen suunta valitaan kahdesta etuviistosektorista.

IsObstacleTooClose

- __init__ luo käyttäytymisen, alustamalla latest_scan arvon sekä tilaa
	sensor_msgs/LaserScan viestejä /scan aiheesta.
- _scan_callback korvaa tallennetun viestin uusimmalla skannauksella.
- update palauttaa aluksi FAILURE jos skannausta ei ole saatu.
- Jokaisen mittauksen kulma lasketaan LaserScan viestin
  angle_min sekä angle_increment arvoista, joka sitten normalisoidaan.
- Silmukka hylkää etusektorin ulkopuoliset kulmat, äärettömät/NaN- sekä
  virheelliset etäisyydet. Alle OBSTACLE_THRESHOLD etäisyys palauttaa
  SUCCESS; muuten lopputulos on FAILURE.

Tämä varmistaa ettei taakse osoittavaa indeksiä 0 tulkita suoraan robotin etupuoleksi.

TurnAway sekä vapaan suunnan valinta

- Konstruktori tilaa /scan aiheen luomalla TwistStamped julkaisijan
	/cmd_vel aiheeseen.
- _sector_clearance palauttaa annetun kulman ympärillä olevan sektorin
  lähimmän kelvollisen mittauksen.
- initialise vertaa vasenta sekä oikeaa etuviistosektoria väistöjakson
  alussa sekä tallentaa väljempään suuntaan viittaavan merkin.
- update julkaisee aikaleimatun viestin. Lineaarinen nopeus on 0.0,
	kulmanopeus on turn_direction * TURN_SPEED sekä status on jatkuvasti RUNNING.

Tämä poikkeaa tehtävänannosta, joka pyytää aina
vasemmalle kääntymistä angular.z = TURN_SPEED. Toteutukseni lisäys
valitsee vasemman tai oikean puolen LiDAR mittausten mukaan. Tämä on tietoinen laajennustoimito.

DriveForward

update julkaisee nykyhetken aikaleiman yhteydessä nopeuden DRIVE_SPEED
eteenpäin sekä kulmanopeuden nollana. Tämä palauttaa RUNNING, koska jatkuva
ajo päättyy vasta kun puu vaihtaa reaktiiviseen haaraan.

hybrid_assignment/task2_tree.py

PatrolTreeNode.__init__ luo ensin IsObstacleTooClose-, TurnAway- sekä
DriveForward-lehdet. Tämän jälkeen puu kootaan seuraavalla tavalla.


reactive_branch = py_trees.composites.Sequence(
		name="Reactive", memory=False,
		children=[obstacle_check, turn],
)
deliberative_branch = py_trees.composites.Sequence(
		name="Deliberative", memory=False,
		children=[drive],
)
root = py_trees.composites.Selector(
		name="Root", memory=False,
		children=[reactive_branch, deliberative_branch],
)


Järjestys tekee väistämisestä etusijaisen. Selector tikkaa Reactive haaran
ensin. memory=False tarkoittaa, että este-ehto tarkistetaan uudelleen
jokaisella kierroksella myös kääntymisen jatkuessa.

- BehaviourTree(root=root) sekä setup(timeout=15) alustavat puun.
- create_timer(1.0 / TICK_RATE_HZ, self._tick) asettaa 10 Hz tikityksen.
- _tick ajaa self.tree.tick() kutsun sekä tulostaa puun tilat
  unicode_tree(..., show_status=True) esityksellä.
- main alustaa ROS 2, pyörittää solmua sekä vapauttaa resurssit
  keskeytyksen jälkeen.

Tässä tiedostossa sekä puun rakentamisen että yhden tulostetun
tilan esteettömällä reitillä sekä yksi väistötilanne.

hybrid_assignment/robot_driver.py

Tämä Webots plugin yhdistää ROS nopeuskomennot TurtleBotin pyörämoottoreihin.

- RobotDriver.__init__ alustaa sisäiset tila-arvot.
- Webots kutsuu init(webots_node, properties) metodia, joka hakee
  vasemman/oikean moottorin sekä pyöräanturit, asettaa moottorit
  nopeusohjaukseen sekä luo ROS tilauksen /cmd_vel aiheeseen.
- __cmd_vel_callback tallentaa uusimman lineaarisen sekä kulmanopeuden.
- step muuntaa nopeudet differentiaalipyörien pyörimisnopeuksiksi
  rajoittamalla ne MAX_SPEED arvolla sekä asettamalla moottorit.
- Pyöräantureiden erot integroidaan sijainniksi sekä suunnaksi.
  Tuloksena Odometry julkaistaan /odom aiheeseen.

/odom auttoi erottamaan julkaistun komennon robotin todellisesta
simuloidusta liikkeestä.

Komentoja terminaaliin

launch/assignment.launch.py

generate_launch_description etsii asennetun paketin jakeluhakemiston sekä
muodostaa polun TurtleBot3Burger.urdf tiedostoon.

- WebotsController liittyy nimettyyn TurtleBot3Burger robottiin sekä
  lukee sen ROS laiteasetukset URDF:stä.
- launch_ros.actions.Node käynnistää paketin task2_tree suoritettavan.
- OnProcessExit sulkee launchin jos Webots controller päättyy.

Tämä on komento, jolla valmis ROS paketti liitetään Webotsissa avoinna
olevaan maailmaan.

resource/TurtleBot3Burger.urdf

URDF ei määrittele robotin koko geometriaa vaan Webots ROS 2 ajurin
laitteiden sekä pluginien ROS asetukset.

- LDS-01 laite julkaisee LaserScan-viestit /scan aiheeseen.
- IMU-plugin julkaisee IMU-dataa /imu aiheeseen.
- hybrid_assignment.robot_driver.RobotDriver liittää oman pyöräajurin
  Webots-robottiin.
- Kamera- sekä syvyyskamera-asetukset ovat mukana laitekonfiguraatiossa,
  mutta tämän tehtävän Behavior Tree käyttää /scan`- sekä  /cmd_vel aiheita.

worlds/break_room.wbt

Tämä on Webotsissa avattava Break Room maailma. Siinä on
TurtleBot3Burger robotti sekä ympäristön seinät, huonekalut ja muut
esteet.

test/test_task1_behaviours.py

FakeRosNode sekä RecordingPublisher korvaavat ROS solmun sekä julkaisijan
testejä, jotta käyttäytymisten viestit voidaan tarkistaa ilman Webotsia.
make_scan luo 360 säteisen skannauksen, jossa indeksi 0 osoittaa taakse.

Testit tarkistavat

- puuttuvan skannauksen sekä vapaan reitin FAILURE tilan
- takana ja etusektorin ulkopuolella olevien esteiden ohittamisen
- etusektorin esteestä palautuvan SUCCESS tilan
- virheelliset sekä kynnysarvon suuruiset mittaukset
- paikallaan kääntävän TurnAway viestin
- oikean tai vasemman suunnan valinnan estettä vastapäätä olevalle
  vapaammalle puolelle
- jatkuvan eteenpäinajon DriveForward viestillä

test/test_task2_tree.py

Pytest-fixture alustaa ROS 2 kontekstin sekä PatrolTreeNode` solmun.
Testiskannaus syötetään suoraan este-ehtoon.

Testit tarkistavat puun Selector/Sequence-rakenteen sekä lapsijärjestyksen,
vapaan reitin DriveForward-haaran, esteen aiheuttaman reaktiivisen
keskeytyksen sekä ajon jatkumisen esteen poistuttua. Timer testi ajaa ROS
executoria varmistamaööa, että puu tikkaa ja tulostaa tilansa.

package.xml, setup.py sekä setup.cfg

- package.xml nimeää ament Python-paketin, ROS ajonaikaiset riippuvuudet
  sekä build tyypin.
- setup.py asentaa Python paketin, launch tiedoston, resurssit sekä
  Webots-maailman. console_scripts määritys luo task2_tree komennon.
- setup.cfg sijoittaa ROS 2 komentoskriptit ament paketin odottamaan
  hakemistoon.

hybrid_assignment/__init__.py sekä resource/hybrid_assignment

Nämä tiedostot ovat tyhjiä merkintätiedostoja. __init__.py
merkitsee Python-moduulin paketiksi, jolloin resurssitiedosto rekisteröi paketin
ament indeksiin. Ne eivät sisällä robotin toiminnallista logiikkaa.

Muut resurssit

- resource/ros2control.yml sekä resource/turtlebot_webots.urdf ovat
	toteutuksessa tyhjiä paikkamerkkejä. Launch sekä TurtleBotin ajuri käyttävät
	resource/TurtleBot3Burger.urdf tiedostoa, joten näitä kahta ei tule
	esittää toimivana ohjauskoodina.
- worlds/.break_room.wbproj tallentaa Webotsin projektinäkymän asetuksia.
	Varsinainen simulaatiomaailma on worlds/break_room.wbt.



Lähteet

1. Tehtävänanto: https://github.com/TEKS4430/Autumn-2026_Assignment_3
2. py_trees Behaviours: https://py-trees.readthedocs.io/en/devel/behaviours.html
3. py_trees Composites: https://py-trees.readthedocs.io/en/devel/composites.html
4. py_trees Trees: https://py-trees.readthedocs.io/en/devel/trees.html
5. py_trees Visualisation: https://py-trees.readthedocs.io/en/devel/visualisation.html
6. ROS 2 Jazzy Topics: https://docs.ros.org/en/jazzy/Concepts/Basic/About-Topics.html
7. Webots ROS 2 -projekti: https://github.com/cyberbotics/webots_ros2
8. Webots R2025a TurtleBot3 Burger: https://github.com/cyberbotics/webots/blob/R2025a/projects/robots/robotis/turtlebot/protos/TurtleBot3Burger.proto
