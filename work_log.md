Module 3 vaiheet


Tehtävänannon lähteet

- Tehtävän README: https://github.com/TEKS4430/Autumn-2026_Assignment_3
- py_trees-käyttäytymiset: https://py-trees.readthedocs.io/en/devel/behaviours.html
- py_trees-komposiitit: https://py-trees.readthedocs.io/en/devel/composites.html
- py_trees-puut: https://py-trees.readthedocs.io/en/devel/trees.html
- py_trees-näkymät: https://py-trees.readthedocs.io/en/devel/visualisation.html



Vaihe 1. py_trees perusteet sekä DriveForward

- Luin tehtävänannon ohjeet käyttäytymien elinkaaresta sekä tiloista, Sequence sekä
  Selector komposiiteista, puun alustamisesta sekä tikkaamisesta unohtamatta puun
  tilan tulostamisesta.
- Vahvistin, että update() palauttaa toiminnallisen tuloksen SUCCESS,
  FAILURE tai RUNNING. Selector valitsee ensimmäisen onnistuvan haaran samaan aikaan kun
  memory=False tarkistaa prioriteetin uudelleen kullakin tikillä.
- Toteutin tehtävänannossa löytyneen DriveForward lehtikäyttäytymisen
  hybrid_assignment/task1_behaviours.py tiedostoon. Tämä julkaisee leimatun
  TwistStamped viestin /cmd_vel aiheeseen nopeudella 0,3 m/s, nollaa
  kulmanopeuden sekä palauttaa RUNNING.
- Lisäsin tiedostoon tehtävänannon säätöarvot seuraavia vaiheita varten.
  este-etäisyys 0,5 m, eteenpäin tarkasteleva puoliavauskulma 30 astetta,
  ajonopeus 0,3 m/s sekä kääntönopeus 0,8 rad/s.

Vaihe. 2 Task 1 lehtikäyttäytymiset

- Toteutin IsObstacleTooClose käyttäytymisen /scan tilauksen sekä uusimman
  LaserScan viestin perusteella. Tämä palauttaa FAILURE jos skannausta ei
  ole tai etusektorilta ei löydy estettä.
- Lasken jokaisen kulman lukeman angle_min sekä angle_increment arvoista. Myös
  normalisoin tämän atan2(sin(angle), cos(angle)) laskulla. Näin indeksiä 0 ei
  oleteta eteenpäin osoittavaksi.
- Tarkastan tehtävänannon FORWARD_ARC_DEG vakiolla määritetyn etusektorin.
  Ohitan äärettömät NaN sekä nolla-/negatiiviset etäisyydet. Estehavainto
  syntyy vain kun hyväksytty etäisyys on aidosti alle OBSTACLE_THRESHOLD arvon.
- Toteutin TurnAway käyttäytymisen julkaisemaan aikaleimatun
  TwistStamped viestin /cmd_vel aiheeseen. Lineaarinen nopeus on 0 eli tila
  on aina RUNNING. Väistöjakson alussa se vertaa LiDAR:in vasenta sekä oikeaa
  60 asteen suuntaan keskitettyä etuviistosektoria eli puoliavaus
  FORWARD_ARC_DEG kääntymällä puolelle, jonka lähin hyväksytty este on
  kauempana. Valittu suunta pidetään samana kyseisen väistöjakson ajan.
  Skannauksen puuttuessa oletus on tehtävänannon mukainen vasemmalle kääntyminen.
- Maailmassa olleen matalan hyllyn vuoksi tarkensin TurnAway käytöstä.
  Aiempi aina vasemmalle komento saattoi ohjata helpommin matalaa hyllyä kohti.
  Vasemmanpuoleinen etuviistoesine valitsee oikealle kääntymisen ja
  oikeanpuoleinen este vasemmalle kääntymisen. Suuntavalinta perustuu
  TURN_SCAN_ANGLE_DEG sekä FORWARD_ARC_DEG vakioihin.
- Lisäsin pytest-testit tiedostoon test/test_task1_behaviours.py.
  Ensimmäinen testiajo paljasti liukulukujen pyöristysongelman täsmälleen
  30 asteen sektorirajalla. Korjasin vertailun math.isclose tarkistuksella.
  Korjauksen jälkeinen testiajo toimi. 14 eri testiä meni läpi, mukana ovat testit molemmille esteen vapaammalle puolelle kääntymiset.
- Korjasin myös testin paketti-importin juurisyyn täyttämällä ament Python paketin
  package.xml, setup.py sekä setup.cfg määritykset. Tämä asentaa
  Python moduulin, resurssit, launch tiedostot, Webots maailman sekä
  task2_tree komentorivimerkinnän.
- Rakensin paketin komennolla colcon build --packages-select
  hybrid_assignment onnistuneella lopputuloksella. Build ilmoitti marker-varoituksen, mutta
  silti ament-indeksimerkki asentui ros2 pkg prefix hybrid_assignment löytämällä paketilla.
- Buildin sekä overlayn lataamisen jälkeen hybrid_assignment.task1_behaviours
  latautuu install hakemistosta ilman käsin lisättyä lähde- PYTHONPATH polkua.

Vaihe 3. Task 2 Behavior Tree

- Toteutin PatrolTreeNode solmun hybrid_assignment/task2_tree.py tiedostoon luomalla kaikki kolme Task 1 lehtikäyttäytymistä.
- Rakensin reaktiivisen Sequence haaran IsObstacleTooClose, TurnAway järjestyksessä sekä
  deliberatiivisen Sequence-haaran, jonka lapsi on DriveForward. Molemmissa Sequence solmuissa on
  memory=False.
- Rakensin juuren Selectoriksi Reactive Deliberative järjestyksessä sekä
  asetin sille memory=False, jotta este-ehto tarkistetaan joka tikillä ennen ajokäyttäytymistä.
- Alustin puun BehaviourTree.setup(timeout=15) kutsulla sekä ajastin tikityksen
  10 Hz:n taajuudelle tulostamalla puun tilan jokaisella tikillä unicode_tree(..., show_status=True) esityksellä. Käynnistyksessä tulostuu myös puun rakenne ilman tämän tiloja.
- Lisäsin neljä Task 2 testiä, jotka tarkistavat puun rakenteen, esteettömän ajon, esteen
  reaktiivisen etusijan sekä ajon jatkumisen esteen hävitessä. Timer-testi ajaa
  ROS-executoria varmistamalla tikityksen sekä tilatulosteen.
- Prioriteetti syntyy Selectorin lapsijärjestyksestä ilman if/else logiikkaa puun kokoamisessa.
- Build onnistui, joten kaikki 18 Task 1–2 testiä menivät läpi
  ros2 pkg executables hybrid_assignment listaamalla komennon komennon task2_tree.

Vaihe 4 Testaus sekä Webots integraatio

- Luin tehtävänannon testausodotukset sekä tarkistin viralliset
  assignment.launch.py, robot_driver.py sekä TurtleBot3Burger.urdf
  tiedostot. Launch käynnistää WebotsControllerin sekä task2_tree solmun.
  URDF liittää LDS-01 /scan aiheeseen sekä ajuri vastaanottaa /cmd_vel
  komennot julkaisemalla /odom odometriaa.
- Täydensin erilliseen hybrid_assignment pakettiin launch-tiedoston,
  Webotsin differentiaalipyöräajurin sekä TurtleBot3 Burgerin URDF. Warehouse-paketin
  lähdetiedostoja ei muutettu.
- Webots controller kytkeytyi onnistuneesti TurtleBot3Burger robottiin.
  Puun konsolitulosteessa esteettömän reitin tila oli tehtävänannon mukainen.
  Reactive epäonnistui, joten Deliberative/DriveForward oli RUNNING.
- ROS aiheiden tarkistus vahvisti /scan tyypiksi sensor_msgs/LaserScan sekä
  /cmd_vel tyypiksi. Webotsilla geometry_msgs/TwistStamped oli /scan
  julkaisija sekä tilaaja puulla.
- /scan virta mitattiin noin 7,3–7,6 Hz tässä container-/simulaatio
  ympäristössä. /cmd_vel sisälsi eteenpäinnopeuden 0,3 m/s sekä nollan
  kulmanopeuden. /odom mittauksessa robotti liikkui vapaan reitin jaksolla
  noin 0,52 m.
- Synkronoidussa ROS testissä julkaistiin lyhyesti 0,2 m eteenpäin osoittava
  LiDAR havainto /scan aiheeseen. Behavior Tree tuotti 22 paikallaan
  kääntävää komentoa linear.x=0, angular.z=0.8. Kun skannaus muutettiin
  vapaaksi inf niin mitatuista 19 nopeuskomennosta kaikki olivat
  eteenpäinajoa linear.x>0.2, angular.z≈0. Täten esteväistö sekä ajon
  jatkuminen testattiin ROS Behavior Tree Webots ohjain ketjussa.
- Dynaamisen puolenvalinnan live testissä pidin etuesteen ja pistin lisäksi
  esteen vasemmalle. 9 havaittua kääntökomentoa suuntautui oikealle
  angular.z=-0.8, linear.x=0. Peilikuvassa oikea este tuotti 9
  vasemmalle kääntyvää komentoa angular.z=+0.8.
- Webots ajurin /odom vahvisti oikealle kääntyvän väistöjakson rungon
  suunnanmuutokseksi noin −0,546 rad 24 odometriaviestin aikana.
- Käyttäjän Webots ajon aikana tekemässä live tarkistuksessa /scan sisälsi
  etusektorilla 60 kelvollista lukemaa. Lähin oli 0,5537 m kulmassa −1,50°,
  eli yli 0,5 m reagointikynnyksen. Samassa näytössä /cmd_vel sisälsi
  11 eteenpäinkomentoa linear.x=0.3, angular.z=0.0 eikä yhtään
  kääntökomentoa. 25 /odom viestin aikana sijainti muuttui 0,1704 m.
  Mittaus vahvisti, että robotti oli silloin jatkanut etenemistä väistäessään esteen.
- Uudessa live tarkistuksessa etusektorin lähin lukema oli 0,5452 m,
  /cmd_vel näytteessä oli kuusi eteenpäinkomentoa eikä kääntökomentoja ja
  19 /odom viestin aikana sijainti muuttui 0,1278 m noin kolmen sekunnin
  näyteikkunassa. Robotti oli tässäkin tarkistushetkessä jatkanut ajoaan.
- Testin lopuksi launch sammutettiin SIGINT:llä. Havaitsin ROS kontekstin
  kaksinkertaisen sammutuksen, joten muutin main() funktion kutsumaan
  rclpy.shutdown() metodia vain mikäli rclpy.ok() on yhä tosi. Uusi
  Webots launchin hallittu sammutustesti ei enää tuottanut tätä poikkeusta.
- Yhtenäistin Webots launchin sekä ajurin sisennykset neljän välilyönnin
  muotoon. Avasin ajurin plugin callbackin tilamuuttujat konstruktorissa sekä
  käsittelin Webotsin pakollisen käyttämättömän parametrin eksplisiittisesti.
  Lopullinen Pylance tiedostoanalyysi sekä yleinen virhelista ovat täten puhtaat.
- Testiskannaus syötettiin ROS aiheeseen testikomennolla. Webots-maailmaan ei
  lisätty tai tallennettu pysyvää esteobjektia. Käyttäjän Webots maailman sisältöä ei myöskään muutettu.
- Kun robotti jumitti vähän väliä niin korvasin aina vasemmalle kääntyvän toiminnon
  vapaan puolen valinnalla. Näin unit-testit varmistavat, että vasemman puolen este tuottaa oikealle ja oikean puolen este vasemmalle kääntävän komennon.
- Dynaamisen väistösuunnan sisältävä uusi launch yritti käynnistyä, mutta
  WebotsController ilmoitti, ettei TurtleBot3Burger ollut enää aktiivisten
  <extern> controllerien listassa. Launch sulkeutui samalla kun controller kuoli.
  Puun koodi taas ei kaatunut. Webots maailman Reset/Reload tarvitaan ennen uutta
  controller yhteyttä aiemman yhteyden katkeamisen jälkeen.
- Tehtävänannon arkkitehtuurikuvauksessa Reactive vastaa välittömään
  LiDAR havaintoon samalla kun Deliberative suorittaa jatkuvaa paikallista ajotavoitetta.

Terminaalin komennot

Tehtävän valmistelussa suoritetut

- find /ros2_ws/src/hybrid_assignment -type f -printf '%P %s bytes\n. Tällä
  tarkistin tehtäväpaketin tiedostorungon.
- code --reuse-window <tiedostopolut>
  Tällä avasin tehtävän tiedostot VS Codeen tarkastelua varten.
- cd /ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select hybrid_assignment
source install/setup.bash
ros2 launch hybrid_assignment assignment.launch.py

Tällä sain yhteyden webots maailmaan, joka saa robotin liikkumaan määrätyillä toiminnoilla.

Lopputuloksen tarkastaminen

- python3 -m py_compile src/hybrid_assignment/hybrid_assignment/task1_behaviours.py
	suoritettu onnistuneesti. käyttäytymistiedoston syntaksi on kelvollinen.
- source /opt/ros/jazzy/setup.bash && colcon build --packages-select hybrid_assignment
	ROS-paketin build onnistui.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && python3 -c "import hybrid_assignment.task1_behaviours; print(hybrid_assignment.task1_behaviours.__file__)" && python3 -m pytest -q src/hybrid_assignment/test/test_task1_behaviours.py
	import ratkesi install hakemistosta ja Task 1 kaikki 12 testiä onnistui ilman
	käsin asetettua PYTHONPATH muuttujaa.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && PYTHONPATH=src/hybrid_assignment:$PYTHONPATH python3 -m pytest -q src/hybrid_assignment/test/test_task2_tree.py
	Task 2 neljä puu sekä timer testiä onnistuivat käytetyssä lähdekoodista.
- source /opt/ros/jazzy/setup.bash && colcon build --packages-select hybrid_assignment && source install/setup.bash && python3 -m pytest -q src/hybrid_assignment/test && ros2 pkg executables hybrid_assignment
	build onnistui kaikki 16 testiä onnistumalla asennetusta paketista sekä
	task2_tree rekisteröityi ROS suoritettavaksi.
- curl -fsSL https://raw.githubusercontent.com/TEKS4430/Autumn-2026_Assignment_3/main/src/hybrid_assignment/launch/assignment.launch.py
	luki virallisen launch tiedoston.
- curl -fsSL https://raw.githubusercontent.com/TEKS4430/Autumn-2026_Assignment_3/main/src/hybrid_assignment/hybrid_assignment/robot_driver.py
	luki virallisen Webots robotin ajurin.
- curl -fsSL https://raw.githubusercontent.com/TEKS4430/Autumn-2026_Assignment_3/main/src/hybrid_assignment/resource/TurtleBot3Burger.urdf
	luki viralliset ROS aiheiden URDF määritykset.
- source /opt/ros/jazzy/setup.bash && python3 -c "from webots_ros2_driver.webots_controller import WebotsController; import inspect; print(WebotsController); print(inspect.signature(WebotsController))"
	varmisti WebotsController luokan saatavuuden sekä portin 1234 oletusarvon.
- python3 -c "import socket; host='host.docker.internal'; print(host, socket.gethostbyname(host)); s=socket.socket(); s.settimeout(2); result=s.connect_ex((host,1234)); print('host Webots-controller port 1234:', 'available' if result == 0 else f'not reachable (errno {result})'); s.close()"
	varmisti host Webotsin controller portin saavutettavuuden devcontainerista.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 launch hybrid_assignment assignment.launch.py
	käynnisti WebotsControllerin sekä Behavior Tree solmun oikeaan avoinna
	olleeseen Webots maailmaan. controller vahvisti robottiliitännän.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 topic info /scan` ja `ros2 topic info /cmd_vel
	tarkisti ROS aiheiden tyypit sekä publisher/subscriber määrät.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && timeout 4s ros2 topic hz /scan
	mittasi LiDAR aiheen taajuuden eli noin 7,3–7,6 Hz.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 topic echo /cmd_vel --once
	tarkisti vapaan reitin nopeuskomennon.
- source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 topic pub --rate 30 --times 50 /scan sensor_msgs/msg/LaserScan "{angle_min: 0.0, angle_increment: 0.0, ranges: [0.2]}"
	kokeilin rajattua esteskannauksen syöttöä. Erillisiin rinnakkaisiin
	terminaaleihin ajoitettu ensimmäinen havainnointi ei ollut ratkaiseva.
	Lopullinen väistö varmentui synkronoidulla alla kuvatulla probe testillä.
- Synkronoidussa ROS probe testissä julkaisin saman solmun 30 Hz timerilla
	este LaserScan viestillä sekä keräsin /cmd_vel viestejä. Tuloksena oli 22
	paikallaan kääntävää komentoa 0,8 rad/s. Vastaavassa vapaan skannauksen
	testissä keräsin 19 eteenpäinajokomentoa esteen hävittyä tieltä.
- /odom probe testissä keräsin 74 odometriaviestiä laskemalla ensimmäisen sekä
	viimeisen sijainnin väliseksi matkaksi 0,5183 m.
- timeout --signal=INT --kill-after=3s 6s ros2 launch hybrid_assignment assignment.launch.py
	testasin uudelleenkäynnistyksen sekä hallitun sammutuksen. Webots controller
	kytkeytyi eikä aiempi kaksinkertaisen rclpy.shutdown() kutsun virhe toistunut.
- python3 -m py_compile src/hybrid_assignment/launch/assignment.launch.py src/hybrid_assignment/hybrid_assignment/robot_driver.py src/hybrid_assignment/hybrid_assignment/task2_tree.py
	Python syntaksitarkistus onnistui.
- source /opt/ros/jazzy/setup.bash && colcon build --packages-select hybrid_assignment && source install/setup.bash && python3 -m pytest -q src/hybrid_assignment/test
	lopullinen build onnistui sekä kaikki 16 testiä läpäistiin myös ajurin
	Pylance siistimisen jälkeen.
- apt-get update päivitti Ubuntun sekä ROS Jazzy paketti indeksit.
- apt-get install -y ros-jazzy-py-trees ros-jazzy-py-trees-ros-interfaces ros-jazzy-py-trees-ros
	asensi ROS Behavior Tree riippuvuudet. Ensimmäinen asennusyritys ennen
	indeksien päivittämistä ei löytänyt paketteja.
- source /opt/ros/jazzy/setup.bash latasi ROS Jazzy ympäristön terminaaliin.
- python3 -m py_compile src/hybrid_assignment/hybrid_assignment/task1_behaviours.py
	syntaksitarkistus onnistui.
- Ajoin DriveForward.update() toiminnon oikealla TwistStamped viestityypillä
	sekä testisolmun valejulkaisijalla. Tarkistin /cmd_vel julkaisijan,
	aikaleiman, lineaarisen nopeuden 0,3 m/s, kulmanopeuden 0,0 rad/s sekä
	RUNNING tilan. kaikki tarkistukset onnistuivat.
- Lisäsin .vscode/settings.json asetukseen ROS Jazzy kirjastopolun, jotta
	Pylance pystyy ratkaisemaan ROS paketit sekä hybrid paketin lähde sekä
	install polun. Tuore Pylance tiedostodiagnostiikka ei ilmoittanut virheitä.
- Runtime testissä PYTHONPATH asetetaan lisäämällä lähdehakemisto ROS
	olemassa olevaan polkuun PYTHONPATH=src/hybrid_assignment:$PYTHONPATH.
	Pelkkä PYTHONPATH=src/hybrid_assignment korvaava ROS hakupolku ei toiminut.

Webotsin ajo-ohje

Avaa Webotsissa src/hybrid_assignment/worlds/break_room.wbt sitten lataa ROS ympäristö sekä käynnistä

cd /ros2_ws
colcon build
source install/setup.bash
ros2 launch hybrid_assignment assignment.launch.py


Varmennustila

- DriveForward, IsObstacleTooClose sekä TurnAway. Toteutettu tehtävänannon
  mukaisesti, jossa TurnAway valitsee avoimemman LiDAR suunnan. 14 Task 1
  kohdennettua testiä läpi.
- Behavior Tree rakennettu tehtävänannon prioriteettijärjestyksessä. Task 2
  neljä testiä ja koko 18 testin sarja läpäisty.
- Testing käyttäytyminen. Vapaan reitin ajo synteettisellä LiDAR havainnolla
  tehty molempiin suuntiin kääntyminen, Webotsin todellinen suuntamuutos sekä
  esteen poistumisen jälkeinen ajon jatkuminen varmennettiin ROS aiheista sekä
  /odom liikkeestä.
- Syntaksi sekä Pylance tiedostodiagnostiikassa ei virheitä uusimmassa
  tiedostoanalyysissä. Yleinen virhekeräin näyttää yhä testitiedoston
  paikallisesta importista ilmoituksen vaikka asennettu moduuli latautuu,
  pytest onnistuu ilman käsin asetettua PYTHONPATH muuttujaa sekä Pylancen
  LSP diagnostiikka on tyhjänä. Lisäpolkuun lisättiin colconin install-
  hakemisto, mutta yleisen virhekeräimen ilmoitus säilyi. Sitä ei peitetty
  muuttamalla toimivaa import lausetta.
- py_trees sekä ROS viestityypit asennettu ROS Jazzyyn sekä runtime testissä
  Käytettävissä kun ROS ympäristö ladataan.
- Webots sekä ROS 2 ajossa launch, robottiliitäntä, LiDAR, nopeuskomennot,
  odometria, esteväistö sekä ajon jatkuminen testattu toimiviksi. Buildissa näkyy edelleen
  colconin marker asennuksen yhteensopivuusvaroitus vaikka paketti asentuu sekä ros2 pkg prefix löytää tämän.