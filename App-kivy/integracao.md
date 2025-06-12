Fechou! Agora que tenho todas as partes da sua API Flask, aqui está o guia completo com **requisições Kotlin para interagir com cada rota** — com destaque para autenticação, envio de arquivos, análise de resposta, e tratamento de token JWT.

---

## 🔐 1. Login – `POST /login`

**Objetivo**: obter o token JWT.

### Kotlin (com `OkHttp` e `Gson`)
```kotlin
val gson = Gson()
val json = gson.toJson(mapOf("username" to "Fala-texto", "password" to "Transcrição_de_fala_em_texto_api"))

val body = json.toRequestBody("application/json".toMediaType())
val request = Request.Builder()
    .url("http://<seu_host>:5000/login")
    .post(body)
    .build()

val response = client.newCall(request).execute()
val token = gson.fromJson(response.body?.string(), Map::class.java)["access_token"] as String
```

---

## 📄 2. Listar Campos do PDF – `POST /listar-campos`

**Protegida com JWT + upload de arquivo PDF**

```kotlin
val file = File("caminho/do/arquivo.pdf")
val requestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
    .addFormDataPart("file", file.name, file.asRequestBody("application/pdf".toMediaType()))
    .build()

val request = Request.Builder()
    .url("http://<seu_host>:5000/listar-campos")
    .addHeader("Authorization", "Bearer $token")
    .post(requestBody)
    .build()

val response = client.newCall(request).execute()
val campos = gson.fromJson(response.body?.string(), Map::class.java)
```

---

## ✍️ 3. Preencher Campos do PDF – `POST /preencher-campos`

**PDF + campos no formato multipart/form-data**

```kotlin
val file = File("documento.pdf")
val formBody = MultipartBody.Builder().setType(MultipartBody.FORM)
    .addFormDataPart("file", file.name, file.asRequestBody("application/pdf".toMediaType()))
    .addFormDataPart("NomeCompleto|7", "João da Silva")   // texto
    .addFormDataPart("Idade|5", "28")                     // inteiro
    .addFormDataPart("Aceita|2", "true")                  // booleano
    .build()

val request = Request.Builder()
    .url("http://<seu_host>:5000/preencher-campos")
    .addHeader("Authorization", "Bearer $token")
    .post(formBody)
    .build()

val response = client.newCall(request).execute()
val pdfBytes = response.body?.bytes()
// Salvar o PDF retornado:
File("preenchido.pdf").writeBytes(pdfBytes!!)
```

---

## 🎙️ 4. Transcrição de Áudio – `POST /transcricao`

**Envia áudio, recebe texto (ou erro)**

```kotlin
val audioFile = File("audio.wav")  // ou .mp3, .m4a, etc.
val requestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
    .addFormDataPart("file", audioFile.name, audioFile.asRequestBody("audio/wav".toMediaType()))
    .build()

val request = Request.Builder()
    .url("http://<seu_host>:5000/transcricao")
    .addHeader("Authorization", "Bearer $token")
    .post(requestBody)
    .build()

val response = client.newCall(request).execute()
val transcricao = gson.fromJson(response.body?.string(), Map::class.java)["text"] as String
```

---

## ✅ 5. Rota Inicial – `GET /`

```kotlin
val request = Request.Builder()
    .url("http://<seu_host>:5000/")
    .get()
    .build()

val response = client.newCall(request).execute()
val mensagem = gson.fromJson(response.body?.string(), Map::class.java)["message"]
```

---

Se quiser, posso organizar isso em um arquivo Kotlin completo, criar uma classe `ApiClient`, adicionar tratamento de erros HTTP, autenticação automática com refresh de token e mais. Quer que a gente leve esse código para o próximo nível? 😄🚀📲
