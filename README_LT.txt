Katalogo kainų programa – gražesnė Streamlit versija

Failai:
- app.py — naršyklinė vartotojo sąsaja
- katalogo_kainu_core.py — pagrindinė logika
- logo.png — logotipas
- requirements.txt — bibliotekos

Paleidimas lokaliai:
1. Įsidiek Python 3.11 arba naujesnį
2. Terminale šiame aplanke vykdyk:
   pip install -r requirements.txt
   streamlit run app.py

Publikavimas internete:
1. Įkelk šiuos failus į GitHub
2. Streamlit Community Cloud pasirink repo ir app.py
3. Deploy

- Parsisiuntimo varnėlės perkeltos po generavimo, prie rezultatų.

- Sugeneruoti rezultatai išsaugomi sesijoje, todėl uždėjus varneles nebeišmeta atgal į generavimo būseną.

- Pašalintos parsisiuntimo varnėlės, palikti tik tiesioginiai mygtukai atsisiuntimui.
