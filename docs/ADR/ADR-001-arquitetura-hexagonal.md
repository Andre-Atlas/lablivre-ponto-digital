# ADR-001: Arquitetura Hexagonal no Backend

- **Status**: Aceita
- **Data**: 2026-09-24
- **Decisores**: Squad de Arquitetura e Engenharia de Backend
- **Contexto Técnico**: Backend FastAPI / Ponto Digital

---

## Contexto

O sistema de registro de ponto eletrônico precisa garantir confiabilidade estrita no cômputo de jornadas, cálculo de horas extras, validações de integridade temporal e conformidade com regras trabalhistas/acadêmicas. Ao longo da evolução do projeto, alterações em frameworks web (ex.: migração ou atualização de FastAPI), drivers de banco de dados (ex.: migração de drivers síncronos para assíncronos, ou transição entre SQLite e PostgreSQL) e provedores de serviços externos (ex.: Google Sheets, notificações por e-mail ou webhook) não devem afetar ou exigir refatorações no núcleo de regras de negócio.

Adicionalmente, arquiteturas tradicionais acopladas diretamente a ORMs como SQLAlchemy dificultam testes unitários rápidos, pois forçam a presença de instâncias de banco de dados mesmo para validar regras lógicas elementares.

---

## Decisão

Adotamos a **Arquitetura Hexagonal (Ports and Adapters)** para estruturar toda a base de código do backend. A aplicação é dividida em três camadas concêntricas bem delimitadas:

1. **`domain/` (Domínio Central)**:
   - Contém entidades puras, objetos de valor (*Value Objects*), exceções de domínio e regras de negócio essenciais.
   - **Zero dependências externas**: não importa FastAPI, SQLAlchemy, bibliotecas de terceiros ou frameworks de transporte.
   - Define interfaces abstratas (*Ports*) para repositórios e serviços externos.

2. **`application/` (Casos de Uso / Portas de Entrada)**:
   - Orquestra o fluxo de dados entre as entidades de domínio e os adaptadores.
   - Implementa os casos de uso do sistema (ex.: `RegistrarPontoUseCase`, `CalcularSaldoHorasUseCase`, `ExportarPlanilhaUseCase`).
   - Define os DTOs de entrada e saída independentes de frameworks web.

3. **`adapters/` e `api/` (Adaptadores de Entrada e Saída)**:
   - **Adaptadores Primários / Conduzentes**: Rotas HTTP com FastAPI (`api/`), controladores e esquemas Pydantic para validação de payload externo.
   - **Adaptadores Secundários / Conduzidos**: Implementações concretas de repositórios com SQLAlchemy (`adapters/database/`), clientes de integração com Google Sheets API (`adapters/sheets/`), hashing de senhas e geradores de token JWT.

```mermaid
flowchart TD
    subgraph DrivingAdapters["Adaptadores Primários (Entrada)"]
        API["FastAPI Routes & Schemas"]
        CLI["Comandos CLI / Scripts"]
    end

    subgraph CoreApplication["Núcleo da Aplicação"]
        subgraph ApplicationLayer["Camada de Aplicação (Use Cases)"]
            UC1["Registrar Ponto"]
            UC2["Calcular Banco de Horas"]
            UC3["Sincronizar Sheets"]
        end

        subgraph DomainLayer["Camada de Domínio (Pura)"]
            Entities["Entidades (RegistroPonto, Colaborador)"]
            Ports["Portas / Interfaces Abstratas (Repositórios)"]
            ValueObjects["Value Objects (Jornada, Horário)"]
        end
    end

    subgraph DrivenAdapters["Adaptadores Secundários (Saída)"]
        RepoPostgres["PostgreSQL / SQLAlchemy 2.0"]
        GoogleSheets["Google Sheets API Adapter"]
        AuthAdapter["JWT & Bcrypt Adapter"]
    end

    DrivingAdapters --> ApplicationLayer
    ApplicationLayer --> DomainLayer
    Ports <|.. DrivenAdapters
    ApplicationLayer --> Ports
```

---

## Consequências

### Positivas
- **Independência Tecnológica**: O domínio permanece isolado de qualquer biblioteca ou framework. Trocar de banco de dados ou de biblioteca de persistência afeta apenas a camada de adaptadores secundários.
- **Altíssima Testabilidade**: Casos de uso e entidades podem ser testados unitariamente em microssegundos utilizando mocks ou repositórios em memória (*Fake Repositories*), sem necessidade de subir contêineres de banco.
- **Substitutibilidade de Adapters**: Permite testar facilmente o fluxo com armazenamento local ou mocks antes de conectar a serviços externos como a API do Google Sheets.
- **Manutenibilidade e Clareza**: Limites explícitos entre responsabilidades técnicas e regras corporativas.

### Negativas / Trade-offs
- **Boilerplate Adicional**: Exige a criação de interfaces abstratas (*protocols* ou classes abstratas `ABC`), mapeadores de DTOs e entidades de domínio distintas das tabelas ORM.
- **Curva de Aprendizado Inicial**: Desenvolvedores acostumados com o modelo padrão "Active Record" ou acoplamento direto no FastAPI precisam se familiarizar com a injeção de dependências e inversão de controle.
