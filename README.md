# songlib

Aplicação web estática: cifras e repertórios via **API pública eIgreja** (`https://eigreja.com/api/public/v1`). Não há cópia local de músicas no repositório.

## Configuração

Edite [`web/js/eigreja-config.js`](web/js/eigreja-config.js) (slug da igreja obrigatório) ou use query string, por exemplo: `index.html?church=seu-slug`.

| Campo | Descrição |
|-------|-----------|
| `churchSlug` | Slug público da igreja no eIgreja |
| `apiBase` | Padrão: `https://eigreja.com/api/public/v1` |
| `syncApiKey` | Opcional; cabeçalho `x-eigreja-api-key` |
| `publicAppUrl` | Base para links de partilha |

## Páginas

| Ficheiro | Função |
|----------|--------|
| `index.html` | Lista de músicas, repertórios, leitor |
| `escolher.html` | Escolha aleatória |
| `roleta.html` | Roleta |
| `relatorio.html` | Estatísticas (Chart.js) |

Requisições: `credentials: 'omit'`. Em outro domínio que não `eigreja.com`, confirme CORS no DevTools.

## Endpoints

- `GET …/musicas?limit=…`
- `GET …/musicas/{id}`
- `GET …/programacoes?limit=…`
