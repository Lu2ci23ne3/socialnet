# SocialNet — Backend (Django + DRF + Channels)

Backend de rede social pronto para ser consumido por um **app nativo (React
Native/Flutter)** ou por um front-end web. Tudo funciona como **API REST +
WebSocket** — não há templates HTML, então o backend só entrega dados em JSON.

## Funcionalidades incluídas

- **Contas**: cadastro, login (JWT), perfil, seguir/deixar de seguir.
- **Posts**: criar/editar/apagar posts (texto + imagem), curtir, comentar.
- **Feed**: geral e personalizado (posts de quem você segue).
- **Chat**: conversas 1-a-1, histórico via REST, mensagens em tempo real via WebSocket.
- **Admin do Django** pronto em `/admin/` para gerenciar tudo visualmente.

## 1. Instalação local

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # ajuste SECRET_KEY antes de ir para produção

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A API sobe em `http://localhost:8000/`.

Para o **WebSocket do chat funcionar**, rode com Daphne (ASGI) em vez do
servidor padrão do Django:

```bash
daphne -b 0.0.0.0 -p 8000 socialnet.asgi:application
```

## 2. Principais endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/api/auth/register/` | Cadastro |
| POST | `/api/auth/login/` | Login (retorna `access` e `refresh` JWT) |
| POST | `/api/auth/refresh/` | Renovar access token |
| GET/PATCH | `/api/auth/me/` | Ver/editar o próprio perfil |
| GET | `/api/auth/users/<username>/` | Perfil público de um usuário |
| POST | `/api/auth/users/<username>/follow/` | Seguir/deixar de seguir |
| GET/POST | `/api/posts/` | Listar todos os posts / criar post |
| GET | `/api/posts/feed/` | Feed personalizado (quem você segue) |
| GET/PATCH/DELETE | `/api/posts/<id>/` | Detalhe / editar / apagar post |
| POST | `/api/posts/<id>/like/` | Curtir/descurtir |
| GET/POST | `/api/posts/<id>/comments/` | Listar/criar comentários |
| GET/POST | `/api/chat/conversations/` | Listar conversas / iniciar uma nova |
| GET/POST | `/api/chat/conversations/<id>/messages/` | Histórico de mensagens |
| WS | `/ws/chat/<id>/?token=<access_token>` | Chat em tempo real |

### Exemplo de fluxo de autenticação

```bash
# Cadastro
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"fernando","email":"f@x.com","password":"SenhaForte123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"fernando","password":"SenhaForte123"}'
# -> {"access": "...", "refresh": "...", "user": {...}}

# Usar o token em requisições autenticadas
curl http://localhost:8000/api/posts/feed/ \
  -H "Authorization: Bearer <access_token>"
```

### Exemplo de uso do WebSocket (JavaScript, para referência ao integrar no app)

```js
const ws = new WebSocket(`ws://localhost:8000/ws/chat/1/?token=${accessToken}`);
ws.onmessage = (event) => console.log(JSON.parse(event.data));
ws.onopen = () => ws.send(JSON.stringify({ content: "Oi!" }));
```

## 3. Próximos passos sugeridos

1. **Conectar o app nativo** (React Native ou Flutter) a estes endpoints —
   posso te ajudar a montar as telas de login, feed e chat assim que você
   escolher a stack do app.
2. **Produção**: trocar SQLite por PostgreSQL, configurar `REDIS_URL` (para
   o chat funcionar com múltiplos servidores) e usar `daphne`/`uvicorn`
   atrás de um proxy como Nginx.
3. **Notificações push** para o app mobile quando chegar mensagem/curtida.
4. **Upload de mídia em produção**: hoje os arquivos vão para `media/`
   local; em produção o ideal é usar S3 ou Cloudinary.

## 4. Estrutura do projeto

```
socialnet/
├── accounts/   # usuários, perfis, seguir/seguidores, JWT
├── posts/      # posts, curtidas, comentários, feed
├── chat/       # conversas, mensagens, WebSocket em tempo real
└── socialnet/  # settings, urls, asgi/wsgi
```
