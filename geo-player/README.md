# geo-player
A deck.gl-based GeoJSON layer animation player with sequenced transitions and camera movements

## Uso

Para abrir la aplicación, abre el archivo `index.html` en tu navegador.

### Parámetros URL

Puedes especificar qué escena cargar mediante el parámetro `scene`:

```
index.html?scene=scenes/01-explanacion-horizontal
```

Si no especificas ningún parámetro, se cargará la escena por defecto: `scenes/01-explanacion-horizontal`

### Estructura de escenas

Cada escena debe estar en su propio directorio y contener:
- `config.json` - Configuración de capas y vista inicial
- `animations.json` - Secuencia de animaciones
- `json/` - Directorio con los archivos GeoJSON de las capas
- `img/` - Directorio con las imágenes utilizadas en las animaciones

### Ejmplos para llamar a una escena

    https://datos1.geoso2.es/geo-player/index.html?scene=scenes/00-ejemplo-basico-pendiente


## Notas para exportación con MAPEXPORT

- MapExport es el comando de autocad que nos permite exportar los elementos seleccionados a un fichero shape. Tenemos varios casos

	En el caso de las curvas de nivel con varios vértices y que tienen la misma altura, 
		1) Se juntan todos los tramos de la curva que tengan la misma cota por medio del comando PEDIT
		2) Se asigna la z en propiedades de la entidad
		3) Se descompone la polilinea en segmentos por medio de EXPLODE
	
	En el caso de un segmento que tiene dos alturas distintas se pueden definir definir en startZ y endZ
	
	En el caso de una circunferencia la convertimos en polígono con tantos lados como queremos. el procedimento es:
		1) Usamos el comando POLYGON
		2) Nos reguntará por el numero de lados (50, por ejemplo)
		3) Elegimos el centro de al circunferencia y metemos la propiedad I ( de inscrito)
		4) Tendremos un polígono. Asignamos altura y le damos a EXPLODE
		
	En el caso de meter texto:
		1) Metemos texto de una sola linea
		2) Le signamos altura
		3) Al exportarlo con MAPEXPORT lo exportamos como texto (no como polígono)
		
	En el caso de meter polígonos (carás cuyos vértices tienen distintas alturas)
		1) usamos el comando 3DPOLI de tl manera que cada vétice tien una sola linea
		2) Cuando lo exportemos con MAPEXPORT exrtarlos como polígonos
		

## Notas para la conversión de shape a json

Lo mejor es utilizar gdal (en windows hacer con WSL, hay que arrancar antes el docker desktop en windows) pongo un par de ejemplos

docker run --rm \
  -v /mnt/c/lim:/data \
  osgeo/gdal:ubuntu-full-3.3.0 \
  ogr2ogr -f GeoJSON -dim 3 \
    /data/repos/geo-player/scenes/00-ejemplo-basico/json/00_B_EXPLANACION_HORIZONTAL_TERRAPLEN_COTAS.json \
    /data/repos/geo-player/scenes/00-ejemplo-basico/sources/00_B_EXPLANACION_HORIZONTAL_TERRAPLEN_COTAS.shp


docker run --rm \
  -v /mnt/c/lim:/data \
  osgeo/gdal:ubuntu-full-3.3.0 \
  ogr2ogr -f GeoJSON -dim 3 \
    /data/repos/geo-player/scenes/01-explanacion-horizontal/json/03-plataforma-terraplen.json \
    /data/repos/geo-player/scenes/01-explanacion-horizontal/sources/03-plataforma-terraplen.shp	
	



