# ADR-002: Flet como Framework de UI do Client Desktop

- **Status**: Aceita
- **Data**: 2026-09-24
- **Decisores**: Squad de Arquitetura e Engenharia Front-End / Desktop
- **Contexto Técnico**: Client Desktop / Ponto Digital

---

## Contexto

O cliente de registro de ponto precisa ser instalado nas estações de trabalho dos colaboradores e alunos da residência, cobrindo com excelência três sistemas operacionais principais: **macOS** (incluindo arquiteturas Apple Silicon ARM64 e Intel x86_64), **Windows 10/11** e distribuições **Linux** (Ubuntu/Debian).

Os requisitos para a aplicação desktop incluem:
1. **Interface Moderna e Polida**: Visual corporativo, suporte nativo a temas (Light/Dark mode), tipografia consistente e transições fluidas sem aspecto de interface antiga ou amadora.
2. **Unificação da Linguagem**: Aproveitar a experiência da equipe em Python, evitando a complexidade de manter bases separadas em C#, Swift ou C++.
3. **Comportamento Confiável Multiplataforma**: Minimizar discrepâncias de renderização de fontes, espaçamentos e componentes de formulário entre macOS, Linux e Windows.
4. **Capacidade de Empacotamento Autônomo**: Geração de binários executáveis (`.app` / `.dmg` no macOS, `.exe` / instalador no Windows, binário `.deb`/AppImage no Linux) que não exijam a pré-instalação manual do interpretador Python nas máquinas dos usuários finais.

Alternativas como Tkinter (visual desatualizado e inconsistente entre plataformas), PyQt/PySide (licenciamento restritivo e curva de estilização complexa) e Electron (consumo elevado de memória com overhead de Node.js + Chromium adicional à stack Python) foram analisadas.

---

## Decisão

Decidimos adotar o **Flet** como framework de interface gráfica para o aplicativo desktop, utilizando o **PyInstaller** e o utilitário `flet pack` / `flet build` para a geração de executáveis distribuíveis.

O Flet permite criar aplicações interativas em Python puro alimentadas pela engine de renderização do **Flutter (Google)**, executada como um processo em segundo plano que comunica com a camada Python via IPC/WebSockets em alta velocidade.

---

## Consequências

### Positivas
- **Consistência Visual Pixel-Perfect**: Graças à engine do Flutter, botões, animações, ícones Material 3 e janelas comportam-se de forma esteticamente impecável em todos os sistemas operacionais.
- **Velocidade de Desenvolvimento**: Desenvolvimento declarativo em Python puro com recarregamento rápido (*hot reload*), sem necessidade de dominar Dart ou JavaScript.
- **Produtividade do Squad**: Desenvolvedores Python transitam facilmente entre o backend e o cliente desktop.
- **Suporte Nativo a Tray e Notificações**: Integração facilitada com a bandeja do sistema operacional (system tray) e notificações locais de ponto.

### Negativas / Trade-offs
- **Tamanho do Binário Final**: Como o Flutter runtime e o interpretador Python embutido via PyInstaller precisam ser incluídos no pacote, o executável final varia tipicamente entre **50 MB e 80 MB**.
- **Consumo de Memória Inicial**: O processo consome um volume de memória moderado (~60-120 MB RAM em execução), aceitável para máquinas corporativas modernas, porém superior a uma interface em C pura.
- **Pipeline de Build Multiplataforma**: A compilação precisa rodar nativamente em runners específicos de cada sistema operacional (macOS runner para build macOS, Windows runner para `.exe`, etc.), o que foi endereçado via matriz de jobs no GitHub Actions.
