# AiTax: Interaktywny Doradca Podatkowy AI (PDD - Project Design Document)

Ten dokument stanowi **kompletny projekt systemu AiTax** — interaktywnego doradcy podatkowego opartego na AI. Opisuje problem, który system rozwiązuje, architekturę techniczną, wykorzystywane technologie, scenariusze użycia oraz plan ewaluacji i demonstracji.

**Cel dokumentu**: Zapewnienie jasnego, szczegółowego widoku całego projektu, na tyle zrozumiałego, że osoba **niezaangażowana w projekt mogłaby**:
- Zrozumieć, jaki problem rozwiązuje system
- Poznać architekturę i przepływ danych
- Odtworzyć demonstrację
- Ocenić jakość i kompletność implementacji

Dokument zawiera zarówno przegląd strategiczny (czemu system jest potrzebny) jak i szczegóły techniczne (jak dokładnie zostanie zaimplementowany).

---

# 1. Przegląd projektu (Overview)

**AiTax** to system doradztwa podatkowego oparty na sztucznej inteligencji, który pomaga użytkownikom zrozumieć obowiązki podatkowe, możliwe odliczenia oraz wymagania raportowania. System łączy **Generację Wzmocnioną Wyszukiwaniem (RAG)** ze **strukturalnym grafem wiedzy podatkowej** do odpowiadania na złożone pytania związane z podatkami.

Aplikacja symuluje **cyfrowego doradcę podatkowego** zdolnego do analizy sytuacji użytkownika i udzielania porad na podstawie regulacji podatkowych. Docelowymi użytkownikami są osoby indywidualne i małe przedsiębiorstwa szukające szybkich, zrozumiałych odpowiedzi na pytania dotyczące podatków (np. "Czy mogę odliczyć wydatki biura domowego?" czy "Ile podatku zapłacę, jeśli zarobię X złotych?").

Główne technologie:
- **LLM (Large Language Model)** do generowania naturalnych odpowiedzi
- **RAG (Retrieval Augmented Generation)** do wyszukiwania relewantnych fragmentów z regulacji
- **Graf Wiedzy** do modelowania strukturalnych relacji między przepisami podatkowymi
- **Python** jako główny język implementacji

Oczekiwany rezultat: Profesjonalny system doradztwa podatkowego oparty na AI, który demonstruje, jak nowoczesne systemy AI mogą uprościć zrozumienie skomplikowanych regulacji prawnych i finansowych dla osób indywidualnych oraz małych przedsiębiorstw.

---

# 2. Opis problemu (Problem Statement)

## Problem

Zrozumienie regulacji podatkowych jest trudne dla osób indywidualnych i małych przedsiębiorstw z następujących powodów:

- Dokumenty prawa podatkowego są złożone i trudne do interpretacji
- Wiele osób nie wie, jakie odliczenia im przysługują
- Przepisy zmieniają się regularnie
- Profesjonalne doradztwo podatkowe jest kosztowne
- Ludzie zwykle potrzebują szybkich odpowiedzi na pytania takie jak:
  - *"Czy mogę odliczyć wydatki biura domowego?"*
  - *"Ile podatku zapłacę, jeśli zarobię 100 000 złotych?"*
  - *"Jakie dokumenty są mi potrzebne do rozliczenia rocznego?"*
  - *"Jakie ulgi podatkowe przysługują studentom?"*

## Rozwiązanie

**AiTax** to system doradztwa podatkowego zasilanego AI, który:

- Wyodrębnia wiedzę z **regulacji podatkowych i dokumentów prawnych**
- Odpowiada na pytania dotyczące podatków w **naturalnym języku**
- Sugeruje **możliwe odliczenia i optymalizacje podatkowe**
- Symuluje **realistyczne scenariusze podatników**
- Dostarcza **wyjaśnień i referencji do regulacji podatkowych**

Rozwiązanie to zmniejsza bariery dostępu do wiedzy podatkowej i pozwala użytkownikom na szybkie uzyskanie porad bez angażowania drogich doradców.

---

# 3. Architektura systemu (System Architecture)

System AiTax składa się z następujących komponentów:

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfejs Użytkownika                    │
│              (Interfejs konwersacyjny / Chat)               │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────v──────────────────────────────────────────┐
│              Warstwa Orkiestracji Zapytań                   │
│          (Przetwarzanie zapytań i orkiestracja agentów)     │
└─────────┬────────────────────────────────────────┬──────────┘
          │                                        │
    ┌─────v──────────┐              ┌──────────────v──────┐
    │  RAG Pipeline  │              │  Wnioskowanie       │
    │  (Wyszukiwanie)│              │  Podatkowe          │
    └─────┬──────────┘              └──────────┬──────────┘
          │                                    │
    ┌─────v──────────────────┐       ┌────────v─────────┐
    │  Baza Wektorowa        │       │  Wiedza          │
    │  (FAISS/Chroma)        │       │  Graf (Neo4j)    │
    │                        │       │                  │
    │ - Osadzenia podatkowe  │       │  - Reguły Pod.   │
    │ - Podzielone dokumenty │       │  - Powiązania    │
    └─────┬──────────────────┘       └────────┬─────────┘
          │                                   │
          └─────────────┬─────────────────────┘
                        │
          ┌─────────────v──────────────┐
          │    LLM (Model Językowy)    │
          │  (OpenAI API / Local)      │
          └─────────────┬──────────────┘
                        │
          ┌─────────────v──────────────┐
          │   Generowanie odpowiedzi   │
          │   i Konstruktor wyjaśnień  │
          └────────────────────────────┘
```

## Komponenty

- **Interfejs Użytkownika**: Interfejs konwersacyjny do komunikacji z systemem
- **Warstwa Orkiestracji**: Przetwarzanie zapytań i koordynacja agentów
- **RAG Pipeline**: Wyszukiwanie relewantnych fragmentów z dokumentów podatkowych w bazie wektorowej
- **Silnik Wnioskowania Podatkowego (Tax Reasoning Engine)**: Logika analizy scenariuszy podatkowych i obliczania wstępnych zobowiązań
- **Baza Wektorowa (Vector Database)**: Przechowywanie osadzonych fragmentów dokumentów o podatkach
- **Graf Wiedzy (Knowledge Graph)**: Modelowanie strukturalnych relacji między przepisami podatkowymi
- **LLM**: Generowanie naturalnych odpowiedzi na podstawie kontekstu
- **Generowanie odpowiedzi**: Budowanie wyjaśnień i referencji do regulacji

---

# 4. Projekt systemu AI (AI System Design)

## LLM

- **Model**: OpenAI GPT-4 (lub lokalne alternatywy takie jak Llama 2 / Mistral)
- **Tryb**: API (OpenAI) lub lokalny (dla pełnej prywatności danych)
- **Rola**: Generowanie naturalnych odpowiedzi na pytania dotyczące podatków, interpretacja scenariuszy użytkownika, dostarczanie wyjaśnień

## System wyszukiwania wiedzy (Retrieval - RAG)

- **Model embeddingów**: OpenAI Embeddings (text-embedding-3-small) lub open-source alternative (all-MiniLM-L6-v2)
- **Baza wektorowa**: FAISS (bezpłatna, lokalna) lub Chroma (również lokalna)
- **Strategia podziału**: Dokumenty podatkowe podzielone na fragmenty o rozmiarze 512-1024 tokenów z zachowaniem kontekstu
- **Metoda wyszukiwania**: Top-K wyszukiwanie (wyszukiwanie 3-5 najbardziej relewantnych fragmentów dla każdego zapytania)

## Wiedza strukturalna (Knowledge Graph)

- **Baza grafowa**: Neo4j
- **Encje**: Przepisy podatkowe, kategorie dochodów, typy odliczeń, scenariusze podatników
- **Relacje**: Zależności między przepisami, warunki dotyczące odliczeń, ograniczenia i wyjątki

## Agenci

### Agent Doradcy Podatkowego (Tax Advisor Agent)
- **Rola**: Główny interfejs do komunikacji z użytkownikiem, odpowiadanie na ogólne pytania podatkowe
- **Narzędzia**: Wyszukiwanie RAG, zapytanie do grafu wiedzy podatkowej, analizator scenariuszy
- **Odpowiedzialność**: Interpretacja pytań, wyszukiwanie odpowiednich przepisów, generowanie odpowiedzi

### Agent Analizy Scenariuszy (Scenario Analysis Agent)
- **Rola**: Analiza sytuacji finansowych użytkownika i obliczanie zobowiązań podatkowych
- **Narzędzia**: Silnik kalkulacji podatków, detektor odliczeń, symulator scenariuszy
- **Odpowiedzialność**: Analiza profilu podatnika, obliczanie przybliżonych podatków, sugerowanie optymalizacji

### Agent Tłumacza Regulacji (Regulation Interpreter Agent)
- **Rola**: Wyjaśnianie złożonych przepisów podatkowych w zrozumiałym języku
- **Narzędzia**: Zapytanie do grafu wiedzy, konstruktor kontekstu
- **Odpowiedzialność**: Uproszczanie legalnego żargonu, dostarczanie przykładów, referowanie do konkretnych paragrafów

## Workflow systemu

Typowy przepływ przetwarzania zapytania użytkownika:

1. **Wejście użytkownika**: Użytkownik zadaje pytanie dotyczące podatków
2. **Analiza zapytania**: System identyfikuje typ pytania (ogólne info, scenariusz, optymalizacja)
3. **Wyszukiwanie informacji**: RAG wyszukuje stosowne fragmenty z dokumentów podatkowych
4. **Budowa kontekstu**: Graf Wiedzy dostarcza powiązane przepisy i warunki
5. **Analiza przez agenta**: Odpowiedni agent (Doradca/Scenariusze/Tłumacz) analizuje zapytanie
6. **Generowanie odpowiedzi**: LLM tworzy naturalną odpowiedź na podstawie zebranego kontekstu
7. **Dodanie wyjaśnień**: System dołącza referencje do konkretnych przepisów i dokumentów
8. **Zwrotna informacja**: Odpowiedź jest prezentowana użytkownikowi wraz z uzasadnieniem

---

# 5. Źródła danych (Data Sources)

## Dokumenty regulacyjne (Tax Regulations)
- **Format**: PDF, tekst
- **Przetwarzanie**: Podział na fragmenty 512-1024 tokenów z zachowaniem kontekstu
- **Przechowywanie**: Baza wektorowa (osadzenia)
- **Cel**: Główne źródło wiedzy dla RAG

## Scenariusze podatników (Taxpayer Scenarios)
- **Format**: Strukturowane dane JSON/CSV
- **Przetwarzanie**: Analiza profilu finansowego, kalkulacja podatków
- **Przechowywanie**: Baza danych (PostgreSQL lub SQLite)
- **Cel**: Testowanie i demonstracja możliwości systemu

## Graf wiedzy podatkowej (Tax Knowledge Graph)
- **Format**: Encje i relacje wyodrębnione z dokumentów
- **Przetwarzanie**: Ekstraktowanie przy pomocy NLP
- **Przechowywanie**: Baza grafowa (Neo4j)
- **Cel**: Modelowanie strukturalnych relacji między przepisami

## Historyczne dane podatkowe
- **Format**: Rzeczywiste wytyczne i przykłady z urzędów skarbowych
- **Przetwarzanie**: Czyszczenie i standaryzacja danych
- **Przechowywanie**: Przeszukiwalna baza grafowa
- **Cel**: Walidacja odpowiedzi systemu

---

# 6. User Stories

### US-1: Zapytanie o zasady gry
Jako osoba indywidualna chcę szybko znaleźć informacje na temat możliwych odliczeń, abym mógł wybrać optymalne rozwiązanie podatkowe.

**Kryteria akceptacji**:
- System wyszukuje relewantne przepisy w bazie wiedzy
- Odpowiedź zawiera konkretne przykłady odliczeń
- Dołączone są referencje do dokumentów źródłowych
- Odpowiedź jest zrozumiała dla osoby bez wiedzy prawniczej

### US-2: Tworzenie profilu podatnika
Jako właściciel małego biznesu chcę wpisać moją sytuację finansową, aby system mógł obliczyć przybliżone podatki, które będę musiał zapłacić.

**Kryteria akceptacji**:
- System akceptuje dane wejściowe zawierające dochód, wydatki, typ biznesu
- System oblicza przybliżoną kwotę podatku
- Wynik pokazuje rozbicie na poszczególne kategorie
- System sugeruje możliwe optymalizacje

### US-3: Generowanie rekomendacji odliczeń
Jako freelancer chcę zobaczyć listę wydatków, które mogę odliczyć z mojego dochodu, abym mógł zminimalizować podatek.

**Kryteria akceptacji**:
- System analizuje profil użytkownika
- Identyfikuje kwalifikujące się odliczenia
- Wyświetla listę wydatków przystosowaną do sytuacji użytkownika
- Dołącza wyjaśnienia dla każdego odliczenia

### US-4: Porównanie scenariuszy podatkowych
Jako student chcę porównać różne opcje rozliczenia podatkowego, aby wybrać najtanszą dla mojej sytuacji.

**Kryteria akceptacji**:
- System pozwala na porównanie scenariuszy "co-jeśli"
- Wyświetla obliczone podatki dla każdego scenariusza
- Wskazuje najlepszą opcję
- Wyjaśnia różnice między wariantami

### US-5: Objaśnianie złożonych przepisów
Jako właściciel firmy chcę, aby trudne przepisy podatkowe były wyjaśnione prostym językiem, abym mógł je zrozumieć bez pomocy doradcy.

**Kryteria akceptacji**:
- System upraszcza złożoną terminologię
- Zawiera konkretne przykłady dotyczące mojej branży
- Wyjaśnienia są dostępne dla osoby bez wiedzy prawniczej
- Dołączone są referencje do oryginalnych tekstów prawnych

### US-6: Dokumentacja wymagań raportowania
Jako samozatrudniony chcę znać dokładne wymagania dotyczące dokumentacji do rocznego rozliczenia, aby byłem przygotowany i uniknął błędów.

**Kryteria akceptacji**:
- System dostarcza pełną listę wymaganych dokumentów
- Lista jest dostosowana do typu dochodów użytkownika
- Zawiera terminy zgłaszania
- Zawiera przykługowe formularze i wytyczne

### US-7: Śledzenie zmian regulacji podatkowych
Jako podatnik chcę być informowany o zmianach w regulacjach, które wpływają na moją sytuację, abym mógł aktualizować moją strategię podatkową.

**Kryteria akceptacji**:
- System wskazuje niedawne zmiany w przepisach
- Wyjaśnia wpływ zmian na konkretną sytuację użytkownika
- Oferuje rekomendacje dotyczące adaptacji do nowych przepisów
- Historia zmian jest dostępna w systemie

### US-8: Interaktywna sesja konsultacyjna
Jako użytkownik chcę przeprowadzić sesję pytań i odpowiedzi z wirtualnym doradcą, aby otrzymać spersonalizowane poradnictwo bez zamawiania spotkania z rzeczywistym doradcą.

**Kryteria akceptacji**:
- System obsługuje wielokrotne pytania w ramach sesji
- Utrzymuje kontekst zmian pomiędzy pytaniami
- Dostosowuje odpowiedzi na podstawie poprzednich pytań użytkownika
- Sesja może być zapisana lub wyeksportowana

---

# 7. Scenariusze użycia (Use Cases)

### UC-1: Zapytanie o zasady odliczeń
**Aktor**: Freelancer

**Opis**: Użytkownik chce dowiedzieć się, jakie wydatki może odliczyć z podatków.

**Kroki**:
1. Użytkownik otwiera system i zadaje pytanie: "Jakie wydatki mogę odliczyć jako freelancer?"
2. System wyszukuje relewantne przepisy dotyczące odliczeń dla samozatrudnionych
3. Wyszukiwanie RAG zwraca 5 najbardziej relewantnych fragmentów z dokumentów podatkowych
4. Agent Doradcy analizuje zapytanie w kontekście znalezionych przepisów
5. LLM generuje odpowiedź zawierającą możliwe kategorie odliczeń
6. System dołącza referencje do konkretnych paragrafów ustawy podatkowej
7. Użytkownik otrzymuje strukturyzowaną listę możliwych odliczeń z wyjaśnieniami

**Oczekiwany rezultat**: Użytkownik ma jasną listę wydatków, które może odliczyć, wraz z warunkami i ograniczeniami.

---

### UC-2: Tworzenie scenariusza podatnika i obliczanie podatków
**Aktor**: Właściciel małego biznesu

**Opis**: Użytkownik chce oszacować wysokość podatku, jaki będzie musiał zapłacić w tym roku.

**Kroki**:
1. Użytkownik podaje informacje o swoim biznesie (typ, roczny dochód, główne wydatki)
2. System analizuje profil podatnika i wyodrębnia kluczowe liczby finansowe
3. Agent Analizy Scenariuszy uruchamia silnik obliczania podatków
4. System konsultuje Graf Wiedzy w celu identyfikacji stawek i ograniczeń podatkowych
5. Podejmuje decyzje dotyczące możliwych dedukcji na podstawie typu biznesu
6. Oblicza przybliżoną kwotę podatku w kilku wariantach (minimum, średnia, zoptymalizowana)
7. System przedstawia rozbicie wyników z sugestią optymalizacji
8. Użytkownik może złożyć pytania uzupełniające na temat konkretnych kwot

**Oczekiwany rezultat**: Użytkownik otrzymuje przybliżone szacunki podatków z wyjaśnieniami i potencjalnymi obszarami oszczędności.

---

### UC-3: Porównanie opcji rozliczenia podatkowego
**Aktor**: Student zarabiający dodatkowy dochód

**Opis**: Użytkownik chce porównać różne formy rozliczenia (ryczałt, skalę, podatek jednostkowy) aby wybrać najtanszą.

**Kroki**:
1. Użytkownik podaje swój roczny dochód
2. System identyfikuje dostępne opcje rozliczenia dla jego sytuacji
3. Agent Analizy Scenariuszy uruchamia scenariusze "co-jeśli" dla każdej opcji
4. Dla każdego scenariusza system oblicza podatki do zapłaty
5. Wyniki są prezentowane w formie porównania (tabela, wykres)
6. System wskazuje opcję z najniższym podatkiem
7. Dołączone są wyjaśnienia różnic między opcjami
8. Użytkownik może zainteresować się szczegółami konkretnej opcji

**Oczekiwany rezultat**: Użytkownik ma jasny obraz kosztów każdej opcji i może podjąć świadomą decyzję dotyczącą formy rozliczenia.

---

### UC-4: Wyjaśnianie złożonych przepisów
**Aktor**: Przedsiębiorca bez wiedzy podatkowej

**Opis**: Użytkownik natrafił na złożony przepis podatkowy i chce go zrozumieć w prostym języku.

**Kroki**:
1. Użytkownik podaje tekst lub powołuje się na konkretny paragraf przepisu
2. System lokalizuje przepis w Grafie Wiedzy i wyszukuje powiązane artykuły
3. Agent Tłumacza Regulacji analizuje tekst i identyfikuje kluczowe koncepty
4. LLM tłumaczy przepis na prosty język dostępny dla laika
5. System dodaje przykłady praktyczne dotyczące branży użytkownika
6. Wyjaśnia każdy kluczowy termin i warunki
7. Dołącza referencje do oryginalnego tekstu dla weryfikacji
8. Oferuje pytania uzupełniające dla dodatkowego wyjaśnienia

**Oczekiwany rezultat**: Użytkownik rozumie złożony przepis i wie, jak wpływa na jego sytuację finansową.

---

### UC-5: Przygotowanie do audytu podatkowego
**Aktor**: Właściciel biznesu podlegającego kontroli

**Opis**: Użytkownik chce przygotować się do audytu poprzez zrozumienie wymagań dokumentacyjnych i potencjalnych problemów.

**Kroki**:
1. Użytkownik podaje informacje, że przechodzi audyt podatkowy
2. System dostarcza listę typowych obszarów egzaminacyjnych dla jego typu biznesu
3. Agent Doradcy identyfikuje potencjalne obszary ryzyka
4. System dostarcza listę dokumentów, które powinny być przygotowane
5. Wyjaśnia, jakie zapisy mogą być kwestionowane
6. Oferuje strategie i wyjaśnienia dla każdego potencjalnego problemu
8. Dostarcza listę kontrolną przygotowania do audytu
9. Umożliwia pytania dotyczące konkretnych obaw

**Oczekiwany rezultat**: Użytkownik ma plan przygotowania do audytu i zrozumienie potencjalnych problemów.

---

# 8. Scenariusze ewaluacji (Evaluation Scenarios)

### Test-1: Wyszukiwanie zasad odliczeń dla freelancerów
**Wejście**:  
"Jakie wydatki mogą odliczyć freelancerzy?"

**Oczekiwane zachowanie**:
- System wyszukuje odpowiednie fragmenty regulacji o odliczeniach
- Generuje odpowiedź z konkretnym liste wydatków (biuro domowe, internet, oprogramowanie itp.)
- Dołącza warunki i ograniczenia dla każdego odliczenia
- Referuje konkretne artykuły kodeksu podatkowego

**Kryteria sukcesu**:  
✓ Odpowiedź zawiera minimum 5 poprawnych kategorii odliczeń  
✓ Zawiera warunki i ograniczenia  
✓ Referuje przepisy

---

### Test-2: Kalkulacja podatków dla konkretnego scenariusza
**Wejście**:  
"Jestem freelancerem zarabiającym 60 000 PLN rocznie. Moje wydatki to: internet (1 200 PLN), oprogramowanie (2 400 PLN), biuro domowe (3 600 PLN na amortyzację). Jaki będzie mój podatek PIT?"

**Oczekiwane zachowanie**:
- System przetwarza dane scenariuszy i wyodrębnia liczby
- Identyfikuje kwalifikujące się odliczenia
- Oblicza dochód netto (60 000 - odliczenia)
- Stosuje poprawne stawki podatkowe (PIT skala podatkowa)
- Oblicza podatek do zapłaty
- Wyświetla rozbicie wyników

**Kryteria sukcesu**:  
✓ Obliczenia są matematycznie poprawne  
✓ Dołączone są objaśnienia dla każdego kroku  
✓ Wyniki są w rozsądnym zakresie

---

### Test-3: Porównanie scenariuszy "co-jeśli"
**Wejście**:  
"Chcę porównać podatek dla ryczałtu 19% vs skalę podatkową dla mojego dochodu 80 000 PLN. Moje wydatki to 20 000 PLN."

**Oczekiwane zachowanie**:
- System oblicza podatek dla opcji ryczałt (80 000 × 19%)
- System oblicza podatek dla skali podatkowej (z odliczeniami)
- Prezentuje wyniki w formie porównania
- Wskazuje, która opcja jest bardziej korzystna
- Wyjaśnia różnice

**Kryteria sukcesu**:  
✓ Oba scenariusze są obliczone poprawnie  
✓ Porównanie jasno wskazuje lepszą opcję  
✓ Wyjaśnienia są zrozumiałe

---

### Test-4: Wyjaśnianie złożonego przepisu
**Wejście**:  
"Wyjaśnij mi art. 21 ust. 1 pkt 139 ustawy o podatku dochodowym od osób fizycznych w prostym języku."

**Oczekiwane zachowanie**:
- System wyszukuje przepis w Grafie Wiedzy
- Upraszcza tekst ustawowy na wyjaśnienie dostępne dla laika
- Dodaje praktyczne przykłady
- Wyjaśnia kluczowe terminy
- Wskazuje potencjalne implikacje dla podatnika

**Kryteria sukcesu**:  
✓ Wyjaśnienie jest zrozumiałe dla osoby bez wiedzy podatkowej  
✓ Zawiera praktyczne przykłady  
✓ Dotyczy konkretnego przepisu

---

### Test-5: Identyfikacja wymaganych dokumentów
**Wejście**:  
"Jakie dokumenty muszę przygotować do rocznego rozliczenia podatkowego jako samozatrudniony?"

**Oczekiwane zachowanie**:
- System generuje listę dokumentów wymaganych dla samozatrudnionych
- Wyjaśnia cel każdego dokumentu
- Podaje terminy zgłaszania
- Zawiera wytyczne dot. przechowywania dokumentów
- Dostarcza listę kontrolną do pobrania

**Kryteria sukcesu**:  
✓ Lista jest kompletna i dokładna  
✓ Zawiera terminy  
✓ Wytyczne są zrozumiałe

---

### Test-6: Analiza scenariusza z wieloma źródłami dochodu
**Wejście**:  
"Jestem nauczycielem-freelancerem zarabiającym 40 000 PLN z pracy i 25 000 PLN z freelancingu. Jakie odliczenia mogę zastosować i jaki będzie mój podatek?"

**Oczekiwane zachowanie**:
- System identyfikuje wiele źródeł dochodów
- Aplikuje reguły odliczeń odpowiednie dla każdego źródła
- Bierze pod uwagę limity i ograniczenia dla łącznych dochodów
- Oblicza podatek na podstawie łącznego dochodu
- Wyświetla rozbicie dla każdego źródła

**Kryteria sukcesu**:  
✓ System obsługuje wielokrotne źródła  
✓ Obliczenia są poprawne dla łącznego dochodu  
✓ Wyjaśnione są reguły dla każdego źródła

---

### Test-7: Sugestia optymalizacji podatkowej
**Wejście**:  
"Mam planowane zarobić 120 000 PLN w tym roku. Czy mogę coś zrobić, aby zmniejszyć swój podatek?"

**Oczekiwane zachowanie**:
- System analizuje potencjalne scenariusze
- Identyfikuje dostępne opcje optymalizacji (wybór formy rozliczenia, zwiększenie wydatków dedukcyjnych, przesunięcie dochodów)
- Oblicza podatek dla każdej opcji
- Rekomenduje najkorzystniejsze podejście
- Wyjaśnia implikacje każdej rekomendacji

**Kryteria sukcesu**:  
✓ Rekomendacje są praktyczne i legalne  
✓ Różnice podatkowe są precyzyjnie obliczone  
✓ Wyjaśnione są potencjalne ryzyka

---

# 9. Ograniczenia systemu (Limitations)

## Halucynacje modelu LLM
Mimo wielowarstwowego systemu kontroli, LLM może czasem generować nieścisłe informacje o przepisach podatkowych. 

**Mitygacja**: Każda odpowiedź zawsze zawiera referencje do konkretnych fragmentów dokumentów źródłowych, które użytkownik może zweryfikować.

---

## Niepełne pokrycie danych
System bazuje na dokumentach podatkowych dostępnych podczas tworzenia. Nowe przepisy lub zmiany regulacyjne mogą nie być odzwierciedlone.

**Mitygacja**: Regularnie aktualizowana baza wiedzy. Dla nowych scenariuszy system wskazuje na potrzebę konsultacji z profesjonalnym doradcą.

---

## Opóźnienia w odpowiedzi (Opóźnienia w Odpowiedzi)
Wyszukiwanie z dużej bazy wektorowej i generowanie odpowiedzi przez LLM może trwać kilka sekund.

**Mitygacja**: Optymalizacja parametrów wyszukiwania, buforowanie odpowiedzi dla częstych pytań, przetwarzanie asynchroniczne.

---

## Ograniczenia modelu LLM
Obecne modele mogą mieć trudności z:
- Bardzo skomplikowanymi scenariuszami z wieloma zmiennymi
- Niszowymi sytuacjami podatkowymi
- Interpretowaniem zmian regulacji w rzeczywistym czasie

**Mitygacja**: Integracja z tradycyjnym silnikiem reguł dla standardowych obliczeń. Dla skomplikowanych przypadków kierowanie użytkownika na konsultacje z doradcą.

---

## Błędy wyszukiwania informacji (Błędy Wyszukiwania)
System RAG może czasami zwrócić nieistotne fragmenty, jeśli zapytanie jest niejasne lub używa innej terminologii.

**Mitygacja**: Ulepszanie inżynierii promptów. Implementacja mechanizmów zapasowych do zarekomendowania alternatywnych źródeł informacji.

---

## Brak spersonalizacji
System dostarcza ogólne poradztwo, ale nie może służyć jako substytut profesjonalnego doradcy podatkowego przygotowanego do konkretnej sytuacji.

**Mitygacja**: Wyraźne zastrzeżenie. Możliwość eksportowania rezultatów do przedłożenia doradcy. Integracja z narzędziami do śledzenia danych finansowych.

---

## Brak obsługi wielljęzyczności
System jest zoptymalizowany na języku polskim. Obsługa języków obcych jest ograniczona.

**Mitygacja**: Możliwość rozszerzenia do obsługi większej liczby języków w przyszłości, jeśli pojawi się taka potrzeba.

---

# 10. Plan demonstracji (Demo Plan)

## Cel demonstracji
Pokazać główne możliwości i zastosowania systemu AiTax dla interaktywnego doradztwa podatkowego.

---

## Przygotowanie środowiska demonstracyjnego

1. **Uruchomienie systemu**: Zapewniania, że wszystkie komponenty (LLM, baza wektorowa, graf wiedzy) działają prawidowo
2. **Przygotowanie danych**: Załadowanie przykładowych dokumentów podatkowych i scenariuszy
3. **Test conectivności**: Sprawdzenie komunikacji między komponentami
4. **Konfiguracja interfejsu**: Upewnianie się, że interfejs jest elastyczny i gotowy do demonstracji

---

## Przebieg demonstracji

### Faza 1: Wprowadzenie i przegląd (2-3 minuty)
- **Pytanie o zasadę odliczeń**
   - Zadanie pytania: "Jakie wydatki może odliczyć freelancer?"
   - Pokazanie: wyszukiwanie RAG, zapytanie do grafu wiedzy, odpowiedź LLM
   - Wynik: Wyświetlenie strukturyzowanej listy odliczeń z referencjami

---

### Faza 2: Prosty scenariusz (3-4 minuty)
- **Tworzenie profilu i obliczanie podatków**
   - Wprowadzenie danych: Dochód 50 000 PLN, wydatki 10 000 PLN
   - System oblicza podatek dla skali podatkowej
   - Pokazanie: Rozbicie wyników, wyjaśnienia dla każdego kroku

---

### Faza 3: Porównanie scenariuszy (3-4 minuty)
- **Porównanie "co-jeśli"**
   - Scenariusz A: Skala podatkowa
   - Scenariusz B: Ryczałt 19%
   - Wyświetlenie: Tabela porównawcza, wskazanie lepszej opcji

---

### Faza 4: Wyjaśnianie przepisów (2-3 minuty)
- **Złożony przepis w prostym języku**
   - Zapytanie o wyjaśnienie konkretnego artykułu
   - Pokazanie: Uproszczone wyjaśnienie, przykłady, terminy
   - Wynik: Użytkownik rozumie przepis

---

### Faza 5: Zaawansowed scenariusz (3-4 minuty)
- **Wielokrotne źródła dochodów**
   - Scenariusz: Nauczyciel + freelancer + działalność gospodarcza
   - System identyfikuje wszystkie źródła
   - Oblicza podatek z uwzględnieniem specyficznych reguł
   - Sugeruje optymalizacje

---

### Faza 6: Pytania i dyskusja (2-3 minuty)
- Odpowiedzenie na pytania dotyczące systemu
- Dyskusja o ograniczeniach i przyszłych rozszerzeniach
- Pokazanie architekektury systemu (jeśli zainteresowanie)

---

## Oczekiwane rezultaty demonstracji

✓ System poprawnie wyszukuje informacje z bazy wiedzy  
✓ Obliczenia podatkowe są dokładne  
✓ Odpowiedzi są zrozumiałe i zawierają referencje  
✓ System obsługuje złożone scenariusze  
✓ Interfejs jest intuicyjny i elastyczny  
✓ Demonstracja pokazuje rzeczywistą wartość systemu dla użytkowników  

---

## Wskazówki do demonstracji

- Przygotować kilka testowych scenariuszy z realistycznymi danymi
- Zapewnić stabilne połączenie internetowe (dla API OpenAI)
- Mieć backup lokalnego LLM w przypadku problemów z API
- Przygotować "slide'y" do wyjaśniania architektury
- Być przygotowanym do pytań zawansowanych o ograniczenia i skalowaniu
- Zanotować czas odpowiedzi systemu dla każdego testu (dokumentacja wydajności)

---

## Postęp demonstracji

|      Faza        |          Opis          |     Czas      |   Status   |
|------------------|------------------------|---------------|------------|
| Przygotowanie    | Konfiguracja i testy   |    -          | Przed demo |
| Wprowadzenie     | Przegląd projektu      | 2-3 min       | Demo       |
| Proste zapytanie | Odliczenia             | 3-4 min       | Demo       |
| Kalkulacja       | Podatek dla wyplaty    | 3-4 min       | Demo       |
| Porównanie       | Scenariusze "co-jeśli" | 3-4 min       | Demo       |
| Wyjaśnianie      | Złożony przepis        | 2-3 min       | Demo       |
| Zaawansowane     | Wiele źródeł           | 3-4 min       | Demo       |
| Q&A              | Pytania i dyskusja     | 2-3 min       | Demo       |
| **Razem**        |           -            | **19-27 min** |      -     |

---

# Addendum: Cele projektu (Success Criteria)

## Wymagania minimalne
- [ ] Zbudowanie bazy wiedzy z dokumentów podatkowych
- [ ] Poprawne odpowiadanie na minimum **15 pytań podatkowych**
- [ ] Symulacja minimum **5 różnych scenariuszy podatników**
- [ ] Dostarczanie wyjaśnień z referencjami do regulacji
- [ ] Kompletna dokumentacja systemu i demonstracja

## Cechy zaawansowane (Bonus)
- [ ] Spersonalizowane sugestie optymalizacji podatkowej
- [ ] Obsługa wielokrotnych źródeł dochodów
- [ ] Symulacje planowania finansowego
- [ ] Wizualne rozbicie kalkulacji podatków
- [ ] Historia sesji i śledzenie scenariuszy

---

# Tech Stack

### Wymagane
- **Python 3.9+** - główny język implementacji
- **LangChain** lub **LlamaIndex** - orkiestracja RAG
- **OpenAI API** - LLM
- **FAISS** lub **Chroma** - baza wektorowa
- **PostgreSQL** lub **SQLite** - przechowywanie strukturalne

### Opcjonalne
- **Neo4j** - graf wiedzy
- **Streamlit** lub **FastAPI** - interfejs aplikacji
- **Pinecone** - skalowalna baza wektorowa
- **LLaMA 2** - lokalna alternatywa do OpenAI

---

# Timeline: 10 tygodni z przeglądem milestone'ów

|   Okres   |           Główny cel            |                Produkty finalne                  |
|-----------|---------------------------------|--------------------------------------------------|
| Tyg. 1-2  | Infrastruktura i baza wiedzy    | Przetworzone dokumenty, baza wektorowa           |
| Tyg. 3-5  | Silnik RAG i Graf Wiedzy       | Działający pipeline RAG, model reguł podatkowych |
| Tyg. 6-8  | Interfejs i agenci              | Conversacyjny interfejs, analiza scenariuszy     |
| Tyg. 9-10 | Testowanie, optymalizacja, demo | Raport ewaluacyjny, demonstracja                 |

---
