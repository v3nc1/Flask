# Flask blog

Jednostavna blog stranica koja ima bazu podataka gdje se spremaju korisnici i njihovi postovi.

Stranica također ima funkciju resetiranja passworda koji na mail šalje token za resetom, ali ta funkcionalnost radi 
samo na mom računalu jer se na mijestu gdje ide username i password od maila koristio modul "os" koji iste podatke
iščitava iz sistemskih Enviroment Variabla.

Korisnici bloga imaju mogučnost dodavanja slike na svoj profil, išćitavanja svojih i tuđih blogova te izmjenu ili brisanje vlastitih blogova.
Dodana je mogučnosti isčitavanja svih blogova od odabranog korisnika klikom na njegovo ime u blogu.
Za registaciju na stranicu korisnik treba preko stranice Register upisati svoj mail, korisničko ime i password. 

Blogovisu poredani od najnovijeg prema najstarijem. Korištena je funkcija Paginate() za prikaz 5 blogova po stranici.

