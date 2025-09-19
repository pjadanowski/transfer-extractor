Es soll eine Python + uv Applikation entwickelt werden, die folgende Aufgaben automatisiert: Authentifizierung via SSH, Herunterladen und Durchsuchen von Logdateien, Extraktion spezifischer Inhalte und Formatierung einer finalen XML-Ausgabe.

#### Die Implementierung umfasst folgende Schritte:

1. SSH-Verbindung zum Zielserver aufbauen:

ssh developer@transfer01.live.bipro.demv.systems

2. Wechsel in das Logverzeichnis:

cd /var/www/bipro-transfer/current/logs

3. Suche nach spezifischen Strings (z. B. "1235435zvcxvsdf") innerhalb ausgewählter Logdateien (Dateinamen enthalten z. B. "jan.log").

4. Bei Treffer: Datei auf das lokale System übertragen. Abhängig von der Dateiendung ggf. Archiv entpacken.

5. In der extrahierten Datei nach dem Schlüsselwort "Response" suchen und das zweite Vorkommen identifizieren.

6. Gefundenen Inhalt in eine separate XML-Ausgabe extrahieren, sauber formatieren und optional als eigenständige Datei abspeichern.

