mapping = {
    "query_parameters": {
        "page": {
            "deutsche_bezeichnung": "Seite",
            "definition": (
                "Gibt an, welche Ergebnis-Seite abgerufen werden soll. Standardmäßig zeigt jede Seite bis zu 500 Spiele. "
                "Mit page=2, page=3, etc. können weitere Spielgruppen abgefragt werden."
            ),
            "anwendung": (
                "Wichtig zur Pagination, wenn mehr als 500 Spiele vorliegen. Damit können umfangreiche Datensätze Stück für Stück "
                "in die Analyse einbezogen werden."
            )
        },
        "max_per_page": {
            "deutsche_bezeichnung": "Maximal pro Seite",
            "definition": (
                "Legt fest, wie viele Spiele maximal pro Seite zurückgegeben werden. Der Standardwert kann erhöht werden, "
                "bis maximal 1000 Spiele."
            ),
            "anwendung": (
                "Ermöglicht es, mehr Spiele in einem API-Aufruf abzurufen – nützlich, wenn ein längerer Analysezeitraum abgedeckt werden soll."
            )
        },
        "max_time": {
            "deutsche_bezeichnung": "Maximale Zeit",
            "definition": (
                "Ein UNIX-Zeitstempel, der angibt, bis zu welchem Zeitpunkt die Statistiken (Liga- und Teamwerte) berücksichtigt werden. "
                "Wird bspw. genutzt, um Ergebnisse nur bis zu einem bestimmten Datum zu analysieren."
            ),
            "anwendung": (
                "Hilfreich, um die Analyse auf einen bestimmten Moment einzugrenzen, beispielsweise um zeitbezogene Veränderungen zu untersuchen."
            )
        },
        "key": {
            "deutsche_bezeichnung": "API-Schlüssel",
            "definition": (
                "Ein eindeutiger Schlüssel, der zum Authentifizieren und Autorisieren des API-Zugriffs benötigt wird."
            ),
            "anwendung": (
                "Unentbehrlich, um sicherzustellen, dass die abgerufenen Daten korrekt und zugelassen sind. Ohne gültigen Schlüssel "
                "ist kein Zugriff auf die Datenbank möglich."
            )
        },
        "season_id": {
            "deutsche_bezeichnung": "Saison ID",
            "definition": (
                "Die eindeutige ID der Liga-Saison, für die die Spielplan-Daten abgerufen werden sollen."
            ),
            "anwendung": (
                "Ermöglicht die gezielte Abfrage und Analyse einer bestimmten Saison, was vor allem in verlaufsbezogenen Analysen "
                "wichtig ist."
            )
        }
    },
    "response_fields": {
        "id": {
            "deutsche_bezeichnung": "Spiel-ID",
            "definition": "Eindeutiger Identifikator eines Spiels in der Datenbank.",
            "anwendung": "Wichtig zur eindeutigen Identifikation und Nachverfolgung einzelner Spiele in der Analyse."
        },
        "homeID": {
            "deutsche_bezeichnung": "Heim-Team-ID",
            "definition": "Eindeutige ID des Heimteams.",
            "anwendung": "Zur Zuordnung der Teamstatistiken des Heimteams und zur Identifikation in Berichten."
        },
        "awayID": {
            "deutsche_bezeichnung": "Gast-Team-ID",
            "definition": "Eindeutige ID des Gastteams.",
            "anwendung": "Zur Zuordnung der Teamstatistiken des Gastteams und zur Identifikation in Berichten."
        },
        "season": {
            "deutsche_bezeichnung": "Saison",
            "definition": (
                "Bezeichnung der Saison (z. B. '2024/2025'), in der das Spiel stattfindet. "
                "Kann als reiner String vorliegen."
            ),
            "anwendung": (
                "Ermöglicht die chronologische Einordnung der Spiele und hilft bei Saisonauswertungen."
            )
        },
        "status": {
            "deutsche_bezeichnung": "Spielstatus",
            "definition": (
                "Zeigt den Status des Spiels an, z. B. 'complete', 'suspended', 'canceled' oder 'incomplete'."
            ),
            "anwendung": (
                "Wichtig, um nur abgeschlossene Spiele in die Analyse einzubeziehen oder um abweichende Fälle zu berücksichtigen."
            )
        },
        "roundID": {
            "deutsche_bezeichnung": "Runden-ID",
            "definition": (
                "Interne ID der Runde, in der das Spiel in der Saison stattfindet."
            ),
            "anwendung": (
                "Hilfreich zur Gruppierung von Spielen, insbesondere wenn mehrere Spiele in einer Runde verglichen werden sollen."
            )
        },
        "game_week": {
            "deutsche_bezeichnung": "Spielwoche",
            "definition": (
                "Die Spielwoche innerhalb der Saison, in der das Spiel stattfindet."
            ),
            "anwendung": (
                "Ermöglicht den Vergleich von Wochenleistungen und die Analyse von Trends über das Saisonverlauf."
            )
        },
        "homeGoals": {
            "deutsche_bezeichnung": "Tore (Heim)",
            "definition": (
                "Liste der Zeitpunkte (in Minuten oder als Zeitangaben), zu denen das Heimteam Tore erzielt hat."
            ),
            "anwendung": (
                "Gibt Aufschluss über den zeitlichen Verlauf der Tore; hilfreich für detaillierte Spielanalysen und Taktikanalysen."
            )
        },
        "awayGoals": {
            "deutsche_bezeichnung": "Tore (Gast)",
            "definition": (
                "Liste der Zeitpunkte, zu denen das Gastteam Tore erzielt hat."
            ),
            "anwendung": (
                "Wie bei den Heimtore, wichtig zur Analyse des Spielverlaufs und taktischer Entscheidungen der Gäste."
            )
        },
        "homeGoalCount": {
            "deutsche_bezeichnung": "Anzahl Tore Heim",
            "definition": "Gesamtzahl der erzielten Tore des Heimteams.",
            "anwendung": "Direkter Vergleich der Offensivleistung des Heimteams."
        },
        "awayGoalCount": {
            "deutsche_bezeichnung": "Anzahl Tore Gast",
            "definition": "Gesamtzahl der erzielten Tore des Gastteams.",
            "anwendung": "Direkter Vergleich der Offensivleistung des Gastteams."
        },
        "totalGoalCount": {
            "deutsche_bezeichnung": "Gesamttoranzahl",
            "definition": "Summe der Tore beider Teams im Spiel.",
            "anwendung": "Wichtig zur Beurteilung der offensiven Intensität und Spielhöhe."
        },
        "team_a_corners": {
            "deutsche_bezeichnung": "Ecken Heim",
            "definition": "Anzahl der Eckbälle, die das Heimteam erhalten hat.",
            "anwendung": "Hilfreich zur Bewertung der Offensivaktionen und des Drucks, den das Heimteam aufgebaut hat."
        },
        "team_b_corners": {
            "deutsche_bezeichnung": "Ecken Gast",
            "definition": "Anzahl der Eckbälle, die das Gastteam erhalten hat.",
            "anwendung": "Dient zur Analyse der Offensivbemühungen des Gastteams."
        },
        "team_a_offsides": {
            "deutsche_bezeichnung": "Abseits (Heim)",
            "definition": "Anzahl der Abseits-Stellungen des Heimteams.",
            "anwendung": (
                "Zeigt, wie oft das Heimteam in eine aggressive Offensive ging, die jedoch zu früh gestartet wurde."
            )
        },
        "team_b_offsides": {
            "deutsche_bezeichnung": "Abseits (Gast)",
            "definition": "Anzahl der Abseits-Stellungen des Gastteams.",
            "anwendung": "Hilfreich zum Verständnis der Offensivstrategien und deren Timing."
        },
        "team_a_yellow_cards": {
            "deutsche_bezeichnung": "Gelbe Karten (Heim)",
            "definition": "Anzahl der gelben Karten, die dem Heimteam erteilt wurden.",
            "anwendung": (
                "Kann Rückschlüsse auf Disziplin und Spielintensität zulassen. Viele gelbe Karten können die Spielweise negativ beeinflussen."
            )
        },
        "team_b_yellow_cards": {
            "deutsche_bezeichnung": "Gelbe Karten (Gast)",
            "definition": "Anzahl der gelben Karten, die dem Gastteam erteilt wurden.",
            "anwendung": "Ebenso wichtig wie für das Heimteam, für Taktikanalysen und Disziplinüberprüfungen."
        },
        "team_a_red_cards": {
            "deutsche_bezeichnung": "Rote Karten (Heim)",
            "definition": "Anzahl der roten Karten, die dem Heimteam angezeigt wurden.",
            "anwendung": (
                "Ein roter Spielerwechsel kann signifikanten Einfluss auf den Spielverlauf und die Taktik haben."
            )
        },
        "team_b_red_cards": {
            "deutsche_bezeichnung": "Rote Karten (Gast)",
            "definition": "Anzahl der roten Karten, die dem Gastteam angezeigt wurden.",
            "anwendung": "Ebenso wichtig für taktische Analysen, da sie häufig zu einem Ungleichgewicht führen."
        },
        "team_a_shotsOnTarget": {
            "deutsche_bezeichnung": "Schüsse aufs Tor (Heim)",
            "definition": "Anzahl der Torschüsse des Heimteams, die ihr Ziel getroffen haben.",
            "anwendung": (
                "Wichtig zur Bewertung der Schussgenauigkeit und Offensivqualität des Heimteams."
            )
        },
        "team_b_shotsOnTarget": {
            "deutsche_bezeichnung": "Schüsse aufs Tor (Gast)",
            "definition": "Anzahl der Torschüsse des Gastteams, die ihr Ziel getroffen haben.",
            "anwendung": "Ermöglicht den Vergleich der Effizienz beider Teams im Abschluss."
        },
        "team_a_shotsOffTarget": {
            "deutsche_bezeichnung": "Schüsse neben (Heim)",
            "definition": "Anzahl der Schüsse des Heimteams, die ihr Ziel verfehlt haben.",
            "anwendung": (
                "Gibt Hinweise auf die Chancenverwertung und kann bei der Analyse von Offensivstrategien helfen."
            )
        },
        "team_b_shotsOffTarget": {
            "deutsche_bezeichnung": "Schüsse neben (Gast)",
            "definition": "Anzahl der Schüsse des Gastteams, die ihr Ziel verfehlt haben.",
            "anwendung": "Ermöglicht Rückschlüsse auf die Chancenverwertung des Gastteams."
        },
        "team_a_shots": {
            "deutsche_bezeichnung": "Gesamte Schüsse (Heim)",
            "definition": "Summe aller Schüsse des Heimteams.",
            "anwendung": "Hilfreich zur allgemeinen Offensivbewertung."
        },
        "team_b_shots": {
            "deutsche_bezeichnung": "Gesamte Schüsse (Gast)",
            "definition": "Summe aller Schüsse des Gastteams.",
            "anwendung": "Erlaubt einen Gesamtüberblick über die Offensivaktivitäten."
        },
        "team_a_fouls": {
            "deutsche_bezeichnung": "Fouls (Heim)",
            "definition": "Anzahl der Fouls des Heimteams.",
            "anwendung": (
                "Nützlich für die Bewertung der Spielintensität und der Fairness des Teams."
            )
        },
        "team_b_fouls": {
            "deutsche_bezeichnung": "Fouls (Gast)",
            "definition": "Anzahl der Fouls des Gastteams.",
            "anwendung": "Ermöglicht Rückschlüsse auf die Aggressivität der Spielweise."
        },
        "team_a_possession": {
            "deutsche_bezeichnung": "Ballbesitz (Heim)",
            "definition": "Prozentsatz des Ballbesitzes des Heimteams.",
            "anwendung": (
                "Wichtig zur Bewertung der Spielkontrolle und Dominanz im Spielverlauf."
            )
        },
        "team_b_possession": {
            "deutsche_bezeichnung": "Ballbesitz (Gast)",
            "definition": "Prozentsatz des Ballbesitzes des Gastteams.",
            "anwendung": "Ermöglicht den Vergleich der Spielkontrolle zwischen den Teams."
        },
        "refereeID": {
            "deutsche_bezeichnung": "Schiedsrichter-ID",
            "definition": (
                "Eindeutige ID des Schiedsrichters, der das Spiel leitet."
            ),
            "anwendung": (
                "Kann bei der Analyse von Schiedsrichterentscheidungen oder Vergleichen zwischen Spielen hilfreich sein."
            )
        },
        "coach_a_ID": {
            "deutsche_bezeichnung": "Trainer-ID (Heim)",
            "definition": "Eindeutige ID des Trainers des Heimteams.",
            "anwendung": "Hilfreich, um performancespezifische Taktiken und Entscheidungen zuzuordnen."
        },
        "coach_b_ID": {
            "deutsche_bezeichnung": "Trainer-ID (Gast)",
            "definition": "Eindeutige ID des Trainers des Gastteams.",
            "anwendung": "Dient dazu, die Strategie und Form beider Trainer zu vergleichen."
        },
        "stadium_name": {
            "deutsche_bezeichnung": "Stadionname",
            "definition": "Offizieller Name des Stadions, in dem das Spiel stattfindet.",
            "anwendung": (
                "Nützlich zur räumlichen Einordnung und für Reports, in denen das Spielumfeld dargestellt wird."
            )
        },
        "stadium_location": {
            "deutsche_bezeichnung": "Stadionsort",
            "definition": "Geographische Lage des Stadions.",
            "anwendung": (
                "Hilfreich, um regionale Einflüsse auf das Spielgeschehen (bspw. Heimvorteil) zu analysieren. "
                "Ist ggf. als leerer String zu behandeln, wenn keine Daten vorliegen."
            )
        },
        "team_a_cards_num": {
            "deutsche_bezeichnung": "Anzahl Karten (Heim)",
            "definition": "Gesamtzahl der Karten (gelb/rot) des Heimteams.",
            "anwendung": "Dient als zusätzlicher Indikator für Disziplin und Spielintensität."
        },
        "team_b_cards_num": {
            "deutsche_bezeichnung": "Anzahl Karten (Gast)",
            "definition": "Gesamtzahl der Karten (gelb/rot) des Gastteams.",
            "anwendung": "Wichtig zum Abgleich mit den Einzelfeldern der gelben und roten Karten."
        },
        "odds_ft_1": {
            "deutsche_bezeichnung": "Quoten (Heimsieg)",
            "definition": "Quote für einen Heimsieg bei Spielende (FT = Full Time).",
            "anwendung": "Relevant, um die Wettmarktmeinung und Risikoeinschätzung für das Heimteam zu analysieren."
        },
        "odds_ft_x": {
            "deutsche_bezeichnung": "Quoten (Unentschieden)",
            "definition": "Quote für ein Unentschieden zum Spielende.",
            "anwendung": "Dient als Indikator der Ausgeglichenheit der Mannschaften im Wettkontext."
        },
        "odds_ft_2": {
            "deutsche_bezeichnung": "Quoten (Gast siegt)",
            "definition": "Quote für einen Gast-Sieg bei Spielende.",
            "anwendung": "Hilfreich zum Vergleich der Siegchancen zwischen Heim- und Gastteam."
        },
        "odds_ft_over05": {
            "deutsche_bezeichnung": "Quote Over 0,5 Tore",
            "definition": "Quote dafür, dass im Spiel mehr als 0,5 Tore erzielt werden.",
            "anwendung": "Nützlich in der Analyse von offensiven Erwartungen."
        },
        "odds_ft_over15": {
            "deutsche_bezeichnung": "Quote Over 1,5 Tore",
            "definition": "Quote dafür, dass im Spiel mehr als 1,5 Tore erzielt werden.",
            "anwendung": "Zeigt die Wettmeinung bezüglich der Torproduktion im Spiel."
        },
        "odds_ft_over25": {
            "deutsche_bezeichnung": "Quote Over 2,5 Tore",
            "definition": "Quote dafür, dass im Spiel mehr als 2,5 Tore erzielt werden.",
            "anwendung": "Hilfreich zur Abschätzung eines torreichen Spiels."
        },
        "odds_ft_over35": {
            "deutsche_bezeichnung": "Quote Over 3,5 Tore",
            "definition": "Quote dafür, dass im Spiel mehr als 3,5 Tore erzielt werden.",
            "anwendung": "Dient zur Bewertung von Spielen mit sehr hoher Torwahrscheinlichkeit."
        },
        "odds_ft_over45": {
            "deutsche_bezeichnung": "Quote Over 4,5 Tore",
            "definition": "Quote dafür, dass im Spiel mehr als 4,5 Tore erzielt werden.",
            "anwendung": "Seltenere Einschätzung, aber hilfreich zur Identifikation von außergewöhnlich torreichen Matches."
        },
        "odds_ft_under05": {
            "deutsche_bezeichnung": "Quote Under 0,5 Tore",
            "definition": "Quote dafür, dass im Spiel weniger als 0,5 Tore erzielt werden.",
            "anwendung": "Indikator für eine sehr geringe Erwartung an die Offensivleistung beider Teams."
        },
        "odds_ft_under15": {
            "deutsche_bezeichnung": "Quote Under 1,5 Tore",
            "definition": "Quote dafür, dass im Spiel weniger als 1,5 Tore erzielt werden.",
            "anwendung": "Dient der Abschätzung eines defensiv geprägten Spiels."
        },
        "odds_ft_under25": {
            "deutsche_bezeichnung": "Quote Under 2,5 Tore",
            "definition": "Quote dafür, dass im Spiel weniger als 2,5 Tore erzielt werden.",
            "anwendung": "Wichtig, um Spielanalysen mit sehr geringer Torquote zu validieren."
        },
        "odds_ft_under35": {
            "deutsche_bezeichnung": "Quote Under 3,5 Tore",
            "definition": "Quote dafür, dass im Spiel weniger als 3,5 Tore erzielt werden.",
            "anwendung": "Gibt einen weiteren Anhaltspunkt für defensiv orientierte Spiele."
        },
        "odds_ft_under45": {
            "deutsche_bezeichnung": "Quote Under 4,5 Tore",
            "definition": "Quote dafür, dass im Spiel weniger als 4,5 Tore erzielt werden.",
            "anwendung": "Wird eher selten genutzt, kann aber als Kennzahl bei Ausreißern dienlich sein."
        },
        "odds_btts_yes": {
            "deutsche_bezeichnung": "Quote BTTS Ja",
            "definition": (
                "Quote dafür, dass beide Teams (Both Teams To Score) mindestens ein Tor erzielen."
            ),
            "anwendung": "Hilfreich, um offensiv-offensiv orientierte Spiele zu identifizieren."
        },
        "odds_btts_no": {
            "deutsche_bezeichnung": "Quote BTTS Nein",
            "definition": (
                "Quote dafür, dass nicht beide Teams ein Tor erzielen."
            ),
            "anwendung": "Dient zur Analyse von Spielen mit dominanter Defensivleistung."
        },
        "odds_team_a_cs_yes": {
            "deutsche_bezeichnung": "Quote Reine Null (Heim, Ja)",
            "definition": (
                "Quote dafür, dass das Heimteam kein Gegentor kassiert (Clean Sheet)."
            ),
            "anwendung": "Wichtig, um die Defensivleistung des Heimteams zu bewerten."
        },
        "odds_team_a_cs_no": {
            "deutsche_bezeichnung": "Quote Reine Null (Heim, Nein)",
            "definition": (
                "Quote dafür, dass das Heimteam ein Gegentor kassiert."
            ),
            "anwendung": "Dient zur Einschätzung der Angriffsstärke des Gegners."
        },
        "odds_team_b_cs_yes": {
            "deutsche_bezeichnung": "Quote Reine Null (Gast, Ja)",
            "definition": (
                "Quote dafür, dass das Gastteam kein Gegentor kassiert."
            ),
            "anwendung": "Relevanter Wert für die Defensivbewertung des Gastteams."
        },
        "odds_team_b_cs_no": {
            "deutsche_bezeichnung": "Quote Reine Null (Gast, Nein)",
            "definition": (
                "Quote dafür, dass das Gastteam ein Gegentor kassiert."
            ),
            "anwendung": "Hilfreich in Kombination mit anderen Offensivwerten."
        },
        "overallGoalCount": {
            "deutsche_bezeichnung": "Gesamtzahl Tore (Alternative)",
            "definition": (
                "Ein alternativer Wert zur Ermittlung der Gesamtzahl der Tore im Spiel. "
                "Kann zur Validierung der Summe aus homeGoalCount und awayGoalCount genutzt werden."
            ),
            "anwendung": "Nützlich für Plausibilitätsprüfungen in der Datenauswertung."
        },
        "ht_goals_team_a": {
            "deutsche_bezeichnung": "Halbzeit Tore (Heim)",
            "definition": "Anzahl der Tore, die das Heimteam in der ersten Halbzeit erzielt hat.",
            "anwendung": "Liefert Ansatzpunkte zur Analyse der Spielentwicklung in der ersten Hälfte."
        },
        "ht_goals_team_b": {
            "deutsche_bezeichnung": "Halbzeit Tore (Gast)",
            "definition": "Anzahl der Tore, die das Gastteam in der ersten Halbzeit erzielt hat.",
            "anwendung": "Wichtig zur Bewertung der frühen Spielperformance."
        },
        "HTGoalCount": {
            "deutsche_bezeichnung": "Halbzeit Gesamtzahl Tore",
            "definition": "Summe der Tore beider Teams in der ersten Halbzeit.",
            "anwendung": "Ermöglicht Vergleiche zwischen Halbzeit- und Endergebnissen."
        },
        "date_unix": {
            "deutsche_bezeichnung": "Spielstart (UNIX)",
            "definition": "UNIX-Zeitstempel, der den Spielanfang angibt.",
            "anwendung": (
                "Erlaubt eine einfache Umrechnung in ein lesbares Datum und damit die zeitliche Einordnung des Spiels."
            )
        },
        "winningTeam": {
            "deutsche_bezeichnung": "Sieger-Team-ID",
            "definition": "ID des Teams, das das Spiel gewonnen hat. Bei Unentschieden oft mit -1 markiert.",
            "anwendung": "Wichtig, um den Ausgang eines Spiels eindeutig zu identifizieren."
        },
        "no_home_away": {
            "deutsche_bezeichnung": "Ohne Heim/Gast-Unterscheidung",
            "definition": (
                "Wird auf 1 gesetzt, wenn es keine Unterscheidung zwischen Heim- und Gastspiel gibt."
            ),
            "anwendung": (
                "Hilfreich bei besonderen Turnierformen oder Freundschaftsspielen, wo diese Differenzierung entfällt."
            )
        },
        "btts_potential": {
            "deutsche_bezeichnung": "BTTS-Potenzial (Pre-Match)",
            "definition": (
                "Vor dem Spiel berechneter Durchschnittswert für beide Teams, Tore zu erzielen (Both Teams To Score)."
            ),
            "anwendung": (
                "Erlaubt eine präventive Einschätzung der Torwahrscheinlichkeit beider Teams bereits vor Spielbeginn."
            )
        },
        "o15_potential": {
            "deutsche_bezeichnung": "Over 1.5 Potential",
            "definition": (
                "Vor dem Spiel berechneter Durchschnittswert für die Wahrscheinlichkeit, dass über 1.5 Tore fallen."
            ),
            "anwendung": (
                "Nützlich zur Abschätzung, ob es sich um ein torreiches Spiel entwickeln könnte."
            )
        },
        "o05HT_potential": {
            "deutsche_bezeichnung": "Over 0.5 HT Potential",
            "definition": (
                "Vor dem Spiel berechneter Wert für die Wahrscheinlichkeit, dass in der ersten Halbzeit über 0.5 Tore erzielt werden."
            ),
            "anwendung": (
                "Gibt frühe Anhaltspunkte zur Offensivleistung der Teams in der ersten Hälfte."
            )
        },
        "corners_potential": {
            "deutsche_bezeichnung": "Ecken Potential",
            "definition": (
                "Durchschnittlicher Erwartungswert für die Anzahl der Ecken beider Teams vor Spielbeginn."
            ),
            "anwendung": "Hilfreich, um Abschätzungen zu zusätzlichen Offensivaktionen zu treffen."
        },
        "offsides_potential": {
            "deutsche_bezeichnung": "Abseits Potential",
            "definition": (
                "Vor dem Spiel berechneter Durchschnittswert für die erwartete Anzahl an Abseits-Positionen beider Teams."
            ),
            "anwendung": "Unterstützt taktische Analysen bezüglich des Offensivdrucks."
        },
        "cards_potential": {
            "deutsche_bezeichnung": "Karten Potential",
            "definition": (
                "Vor dem Spiel berechneter Wert für die erwartete Kartenanzahl (gelb/rot) in einem Spiel."
            ),
            "anwendung": "Ermöglicht eine Einschätzung, wie intensiv das Spiel eventuell in Bezug auf Fouls und Strafen geführt wird."
        },
        "avg_potential": {
            "deutsche_bezeichnung": "Durchschnittliche Tore (Potential)",
            "definition": (
                "Der vor dem Spiel berechnete Durchschnitt der erwarteten Tore beider Teams."
            ),
            "anwendung": (
                "Relevant für Prognosen und Wettanalysen, um das erwartete Spieltempo einzuschätzen."
            )
        },
        "home_ppg": {
            "deutsche_bezeichnung": "Punkte pro Spiel (Heim)",
            "definition": (
                "Aktueller Durchschnitt der vom Heimteam erzielten Punkte pro Spiel."
            ),
            "anwendung": "Wichtig zur Bewertung der aktuellen Form des Heimteams."
        },
        "away_ppg": {
            "deutsche_bezeichnung": "Punkte pro Spiel (Gast)",
            "definition": (
                "Aktueller Durchschnitt der vom Gastteam erzielten Punkte pro Spiel."
            ),
            "anwendung": "Vergleichsgröße zur Bestimmung der Ausgeglichenheit beider Teams."
        },
        "pre_match_home_ppg": {
            "deutsche_bezeichnung": "Pre-Match Punkte pro Spiel (Heim)",
            "definition": (
                "Punkte pro Spiel des Heimteams, bevor das aktuelle Spiel stattfindet. "
                "Kann als Referenzwert dienen."
            ),
            "anwendung": "Hilft, Formschwankungen vor Spielbeginn zu erkennen."
        },
        "pre_match_away_ppg": {
            "deutsche_bezeichnung": "Pre-Match Punkte pro Spiel (Gast)",
            "definition": (
                "Punkte pro Spiel des Gastteams vor Spielstart."
            ),
            "anwendung": "Nützlich zum Vergleich der Teamleistung vor dem Spiel."
        },
        "competition_id": {
            "deutsche_bezeichnung": "Wettbewerbs-ID",
            "definition": (
                "Die ID des Wettbewerbs bzw. der Saison, in der das Spiel ausgetragen wird."
            ),
            "anwendung": "Ermöglicht, Spiele einer bestimmten Liga oder Saison zu gruppieren."
        },
        "over05": {
            "deutsche_bezeichnung": "Over 0,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob mehr als 0,5 Tore im Spiel erzielt wurden."
            ),
            "anwendung": "Hilfreich zur Kategorisierung von Spielen als torreich."
        },
        "over15": {
            "deutsche_bezeichnung": "Over 1,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob mehr als 1,5 Tore erzielt wurden."
            ),
            "anwendung": "Ermöglicht eine grobe Klassifikation des Spielausgangs bezüglich der Toranzahl."
        },
        "over25": {
            "deutsche_bezeichnung": "Over 2,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob mehr als 2,5 Tore im Spiel gefallen sind."
            ),
            "anwendung": "Wichtig, um torreiche Spiele einzuordnen."
        },
        "over35": {
            "deutsche_bezeichnung": "Over 3,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob mehr als 3,5 Tore erzielt wurden."
            ),
            "anwendung": "Hilfreich für die Identifikation von außergewöhnlich offensiven Spielen."
        },
        "over45": {
            "deutsche_bezeichnung": "Over 4,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der festlegt, ob mehr als 4,5 Tore erzielt wurden."
            ),
            "anwendung": "Selten genutzt, kann aber bei der Identifikation von Extremfällen hilfreich sein."
        },
        "over55": {
            "deutsche_bezeichnung": "Over 5,5 Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob mehr als 5,5 Tore erzielt wurden."
            ),
            "anwendung": "Wird verwendet, um extrem torreiche Spiele ausfindig zu machen."
        },
        "btts": {
            "deutsche_bezeichnung": "BTTS Endergebnis",
            "definition": (
                "Boolescher Wert, der angibt, ob beide Teams mindestens ein Tor erzielt haben."
            ),
            "anwendung": "Relevant zur Analyse von Spielen, in denen beide Mannschaften offensiv aktiv waren."
        }
    },
    "unmapped_fields": {
        "revised_game_week": {
            "deutsche_bezeichnung": "Revidierte Spielwoche",
            "definition": (
                "Falls vorhanden, zeigt dieser Wert eine angepasste Spielwoche, etwa durch Verschiebungen oder Neuplanungen."
            ),
            "anwendung": (
                "Kann zur Validierung herangezogen werden, wenn offizielle Spielwochen von denen im System abweichen. "
                "Ein negativer Wert kann als Platzhalter interpretiert werden."
            )
        },
        "totalCornerCount": {
            "deutsche_bezeichnung": "Gesamte Eckballanzahl",
            "definition": (
                "Summe der Eckbälle beider Teams. Dient der Validierung der Einzelwerte."
            ),
            "anwendung": (
                "Nützlich zur Überprüfung, ob die Summe der einzelnen Eckzahlen (Heim + Gast) stimmig ist."
            )
        }
        # Hier könnten weitere nicht zugeordnete Felder ergänzt werden, z. B. zusätzliche Wettquoten (doublechance, Halbzeitergebnisse, etc.)
    }
}

# Ausgabe des Mappings als JSON-ähnliche Struktur
import json
with open("league-matches-mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
# print(json.dumps(mapping, indent=4, ensure_ascii=False))
