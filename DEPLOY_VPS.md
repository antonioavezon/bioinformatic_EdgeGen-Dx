# Guía de Despliegue en VPS (Fedora/Linux)

Dado que ya tienes un VPS con Fedora y contenedores funcionando, la forma más limpia es usar **Docker** (o Podman) para levantar EdgeGen-Dx en un puerto paralelo.

## Paso 1: Clonar el Repositorio en el VPS
Conéctate por SSH a tu servidor y clona el proyecto:
```bash
git clone https://github.com/antonioavezon/bioinformatic_EdgeGen-Dx.git
cd bioinformatic_EdgeGen-Dx
```

## Paso 2: Construir la Imagen
Construye la imagen Docker. Esto instalará todas las dependencias aisladas de tu otra app.
```bash
docker build -t edgegen-dx:v1 .
```

## Paso 3: Ejecutar el Contenedor
Aquí está el truco: mapearemos el puerto interno `8000` a un puerto externo libre en tu VPS, por ejemplo, el **8081**.

```bash
docker run -d \
    --name edgegen-app \
    --restart unless-stopped \
    -p 8081:8000 \
    edgegen-dx:v1
```

*   `-d`: Ejecutar en segundo plano (detached).
*   `--restart unless-stopped`: Si el VPS se reinicia, la app vuelve a arrancar.
*   `-p 8081:8000`: Accederás por el puerto 8081.

## Paso 4: Configurar Firewall (Si es necesario)
Si usas `firewalld` en Fedora, asegúrate de abrir el puerto:
```bash
sudo firewall-cmd --permanent --add-port=8081/tcp
sudo firewall-cmd --reload
```

## Paso 5: Acceso
Ahora deberías poder entrar desde tu navegador:
`http://TU_IP_VPS:8081`

¡Listo! Tienes EdgeGen-Dx corriendo en paralelo sin tocar tu configuración existente.
