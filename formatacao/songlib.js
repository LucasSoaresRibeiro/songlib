//https://songlib.com/sets/4297/*/song/*/

whats_msg = [];

function YouTubeGetID(url) {
	try {
	   url = url.split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
	   return (url[2] !== undefined) ? url[2].split(/[^0-9a-z_\-]/i)[0] : url[0];
	}
   catch {
   	return null;
   }
}

if (!String.prototype.format) 
{
    String.prototype.format = function()
    {
        var args = arguments;

        if (typeof args[0] != "object")
        {
            return this.replace(/{\d+}/g, function(m)
            {
                var index = Number(m.replace(/\D/g, ""));
                return (args[index] ? args[index] : m);
            });
        }
        else 
        {
            var obj = args[0],
                keys = Object.keys(obj);

            return this.replace(/{\w+}/g, function(m)
            {
                var key = m.replace(/{|}/g, "");
                return (obj.hasOwnProperty(key) ? obj[key] : m);
            });
        }
    };
}

function httpGet(url)
{
    var xmlHttp = null;

    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", url, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

console.log("Aguarde, unindo musicas...");

var baseUrl = "https://songlib.com/";
var songs = document.getElementsByClassName("load-song-only");

var songDatas = [];

// get song properties
for (let index = 0; index < songs.length; index++) {
    const song = songs[index];
    // console.log(song.getAttribute("data-ajax-href"));
    const songId = song.getAttribute("data-songid");
    
    var keyElement = song.parentElement.getElementsByTagName("span")[0];
    var key = "";
    if (keyElement) {
        key = song.parentElement.getElementsByTagName("span")[0].innerText;
    };
    
    // song properties
    let linkRef = null;
    let timeSig = null;
    let notes = null;
    try {
	    var songPropertiesUrl = `${baseUrl}/songs/4297/${songId}/properties/ajax/`;
	    var songPropertiesResponse = httpGet(songPropertiesUrl);
		const tempElement = document.createElement('div');
		tempElement.innerHTML = songPropertiesResponse;
		// Find the <th> element with the text "URL"
		const thElements = tempElement.querySelectorAll('th');
		
		let tdElementUrl;
		thElements.forEach((thElement) => {
			if (thElement.textContent.trim() === 'URL') {
			    tdElementUrl = thElement.nextElementSibling;
			    linkRef = tdElementUrl.firstChild?.href ? tdElementUrl.firstChild?.href : null;
			}
			if (thElement.textContent.trim() === 'Time sig') {
				tdElementUrl = thElement.nextElementSibling;
		    	timeSig = tdElementUrl.firstChild?.textContent ? tdElementUrl.firstChild?.textContent : null;
			}
			if (thElement.textContent.trim() === 'Notes') {
				tdElementUrl = thElement.nextElementSibling;
		    	notes = tdElementUrl.firstChild?.textContent ? tdElementUrl.firstChild?.textContent : null;
			}
		});

    } catch {
    	
    }

    var name = song.innerText.trim()
    var songData = {
        "url": song.getAttribute("data-ajax-href"),
        "name": name,
        "key": key.substring(2),
        "linkRef": linkRef,
        "timeSig": timeSig,
        "notes": notes,
    };
    songDatas.push(songData);
}

var divPage = document.getElementsByClassName("page")[0];
divPage.innerHTML = "";

// CAPA
console.log("Adicionando sumário");
var response = httpGet(baseUrl+songDatas[0].url);
var jsonResponse = JSON.parse(response);
var htmlHeader = "";

// CAPA - LOGO
htmlHeader += "<h2></h2>";
htmlHeader += '<img width="450px" src="https://static.wixstatic.com/media/a58031_21b005a3dc204ce1aa6e3bd8368e5865~mv2.png">';
htmlHeader += "</br>";

// CAPA - TITULO REPERTORIO
htmlHeader += "<hr></hr>";
htmlHeader += "<h3>{0}</h3>".format(jsonResponse.set.title);
whats_msg.push(jsonResponse.set.title);

var date = new Date(jsonResponse.set.date);
date_str = `${date.getUTCDate()}/${date.getUTCMonth()+1}/${date.getUTCFullYear()}`;
whats_msg.push(`Data: ${date_str}`);

htmlHeader+= `<p class='cover-date'>Data: ${date_str}</p>`;
htmlHeader += "</br>";
htmlHeader += "<hr></hr>";

// CAPA - LISTA DE MUSICAS
htmlHeader += "<h3>Músicas:</h3>";
for (let index = 0; index < songDatas.length; index++) {
    htmlHeader+= `<p class='cover-music-name'>${songDatas[index].name} - <span class='cover-key'>${songDatas[index].key}</span></p>`;
    // htmlHeader+= `<p><a class="cover-link" href="${songDatas[index].linkRef}" target="_blank"></a></p>`;
    
    whats_msg.push('');
    whats_msg.push(`${songDatas[index].name}`);
    // whats_msg.push(`Tom: ${songDatas[index].key}`);
    whats_msg.push(`${songDatas[index].linkRef}`);
}

// CAPA - Playlist
htmlHeader += "<hr></hr>";
htmlHeader += "<h4>Playlist de Referência:</h4>";
let videoIds = []
for (let index = 0; index < songDatas.length; index++) {
	let videoId = YouTubeGetID(songDatas[index].linkRef);
	if (videoId != null) {
		videoIds.push(videoId);
	}
}
let playlistLink = `http://www.youtube.com/watch_videos?video_ids=${videoIds}&start_radio=1`;
htmlHeader += `<p><a class="cover-playlist-link" href="${playlistLink}" target="_blank"></a></p>`;

// CAPA - Playlist QRCode
htmlHeader += `<img width="150px" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${playlistLink}">`;

// CAPA - Insere HTML
var htmlObject = document.createElement('div');
htmlObject.innerHTML = htmlHeader;
divPage.appendChild(htmlObject);

// TITULO ARQUIVO
var dataRepertorio = "{0}{1}".format(("0" + (date.getUTCMonth()+1)).slice(-2), ("0" + date.getUTCDate()).slice(-2));
document.title = "IBM-{0}-{1}".format(dataRepertorio, jsonResponse.set.title);

// songs
for (let index = 0; index < songDatas.length; index++) {
    var response = httpGet(baseUrl+songDatas[index].url);
    
    response = response.replace("Written by <b>","Versão: ");
    //console.log(response);
    var jsonResponse = JSON.parse(response);
    //console.log(jsonResponse.chords.headerHtml);

    console.log("Adicionando "+jsonResponse.song.title);

    // CABEÇALHO DA MÚSICA
    var htmlObject = document.createElement('div');
    htmlObject.innerHTML = jsonResponse.chords.headerHtml;
    divPage.appendChild(htmlObject);
    
    // LOGO / TIMBRE
	var htmlObject = document.createElement('div');
    htmlObject.innerHTML = '<img class="church-logo" src="https://static.wixstatic.com/media/a58031_21b005a3dc204ce1aa6e3bd8368e5865~mv2.png">';
    divPage.appendChild(htmlObject);
    
    // TONALIDADE
	let toneHtmlContent = `<p>Tom: <span class='key'>${songDatas[index].key}</span>`;
	
	// COMPASSO
    if (songDatas[index].timeSig) {
    	toneHtmlContent += ` | Compasso: ${songDatas[index].timeSig}`;
    }
    
    // REFERENCIA
    if (songDatas[index].linkRef) {
    	toneHtmlContent += ` | <span class="link">REFERÊNCIA: <a href="${songDatas[index].linkRef}" target="_blank"></a></span>`;
    }
    
    toneHtmlContent += '</p>' ;
    var htmlObject = document.createElement('div');
    htmlObject.innerHTML = toneHtmlContent;
    divPage.appendChild(htmlObject);

    // ACORDES
    var htmlObject = document.createElement('div');
    htmlObject.innerHTML = jsonResponse.chords.chordsHtml;
    divPage.appendChild(htmlObject);
}

// Adiciona estilo customizado para o heading de repetição
const headingElements = document.querySelectorAll('.heading');
console.log(headingElements);

headingElements.forEach((headingElement) => {
	if (headingElement.innerText.endsWith("...")) {
		headingElement.classList.remove("heading");
		headingElement.classList.add("heading-repetition");
	}
});

// send whats app message
whats_url = `https://api.whatsapp.com/send/?phone=12982348140&text=${encodeURI(whats_msg.join('\n'))}&type=phone_number&app_absent=0`;
console.log(whats_url);

console.log("finalizado!");
window.print();

setTimeout(function() {
	window.open(whats_url);
}, 1000);