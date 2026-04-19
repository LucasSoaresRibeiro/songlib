//https://songlib.com/sets/4297/*/song/*/

whats_msg =[];

function YouTubeGetID(url) {
	try {
	   url = url.split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
	   return (url[2] !== undefined) ? url[2].split(/[^0-9a-z_\-]/i)[0] : url[0];
	}
   catch (e) {
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

var songDatas =[];

// get song properties
for (let index = 0; index < songs.length; index++) {
    const song = songs[index];
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
			    var fc0 = tdElementUrl.firstChild;
			    linkRef = fc0 && fc0.href ? fc0.href : null;
			}
			if (thElement.textContent.trim() === 'Time sig') {
				tdElementUrl = thElement.nextElementSibling;
		    	var fc1 = tdElementUrl.firstChild;
		    	timeSig = fc1 && fc1.textContent ? fc1.textContent : null;
			}
			if (thElement.textContent.trim() === 'Notes') {
				tdElementUrl = thElement.nextElementSibling;
		    	var fc2 = tdElementUrl.firstChild;
		    	notes = fc2 && fc2.textContent ? fc2.textContent : null;
			}
		});

    } catch (e) {

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

// CAPA - TITULO REPERTORIO E WHATSAPP MSG HEADER
htmlHeader += "<hr></hr>";
htmlHeader += "<h3>{0}</h3>".format(jsonResponse.set.title);
whats_msg.push(`*${jsonResponse.set.title}*`);

var date = new Date(jsonResponse.set.date);
date_str = `${("0" + date.getUTCDate()).slice(-2)}/${("0" + (date.getUTCMonth()+1)).slice(-2)}/${date.getUTCFullYear()}`;
whats_msg.push(`📅 *Data:* ${date_str}`);

htmlHeader+= `<p class='cover-date'>Data: ${date_str}</p>`;
htmlHeader += "</br>";

// CAPA - LISTA DE MUSICAS (HTML PREServado)
for (let index = 0; index < songDatas.length; index++) {
    htmlHeader+= `<p class='cover-music-name'>${songDatas[index].name} - <span class='cover-key'>${songDatas[index].key}</span></p>`;
    if (songDatas[index].linkRef) {
    	songDatas[index].linkRef.split("|").forEach(link =>
    		{
					htmlHeader+= `<p><a class="cover-link" href="${link.trim()}" target="_blank"> </a></p>`;
    		}
  		)
    }
}

// --- NOVA LÓGICA DO WHATS_MSG (Formatado, Múltiplos Links e Sem Numeração) ---
let urlGroups = {};
let noUrlSongs =[];

songDatas.forEach(song => {
    let cleanName = song.name;
    // Exclui o número da música identificando padrões comuns (ex: "1 - ", "02. ", etc)
    let numMatch = cleanName.match(/^(\d+)[\s\.\-\)]+/);
    if (numMatch && parseInt(numMatch[1], 10) < 100) {
        cleanName = cleanName.substring(numMatch[0].length).trim();
    }

    if (song.linkRef) {
        // Extrai e limpa os links do separador |
        let links = song.linkRef.split('|').map(l => l.trim()).filter(l => l);
        
        if (links.length > 0) {
            // Cria uma chave única baseada na combinação de links ordenados
            let groupKey = links.slice().sort().join('|');
            if (!urlGroups[groupKey]) {
                urlGroups[groupKey] = {
                    songs:[],
                    links: links // Guarda os links separados em array para listagem visual
                };
            }
            urlGroups[groupKey].songs.push(cleanName);
        } else {
            noUrlSongs.push(cleanName);
        }
    } else {
        noUrlSongs.push(cleanName);
    }
});

whats_msg.push('');

// Preenche a mensagem listando a música (ou agrupamento) e as múltiplas URLs logo abaixo
Object.values(urlGroups).forEach(group => {
    // Une as músicas caso partilhem das mesmíssimas URLs
    let songNames = [...new Set(group.songs)].join(' / ');
    whats_msg.push(`*${songNames}*`);
    
    // Imprime os links um abaixo do outro
    group.links.forEach(link => {
        whats_msg.push(`- ${link}`);
    });
    whats_msg.push('');
});

// Adiciona as músicas que ficaram sem URL
if (noUrlSongs.length > 0) {
    let songNames = [...new Set(noUrlSongs)].join(' / ');
    whats_msg.push(`*${songNames}*`);
    whats_msg.push(`_Sem URL de referência_`);
    whats_msg.push('');
}
// --- FIM DA LÓGICA DO WHATS_MSG ---

// CAPA - Playlists
htmlHeader += "<div style='display: flex; justify-content: space-around; align-items: flex-start; margin-top: 10px;'>";

// Online Playlist Section
const setId = window.location.pathname.split('/')[3];
const onlinePlaylistUrl = `https://equipedelouvor.com/?set=${setId}`;

htmlHeader += "<div style='width: 50%; overflow-wrap: break-word;page-break-inside: avoid;'>";
htmlHeader += "<h4 style='margin-bottom: -12px; margin-top: 10px;'>Cifra online:</h4>";
htmlHeader += "<div style='display: flex; align-items: center;'>";
htmlHeader += `<img width="100px" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${onlinePlaylistUrl}">`;
htmlHeader += `<a class="cover-playlist-link" href="${onlinePlaylistUrl}" target="_blank" style="margin-left: 10px;"></a>`;
htmlHeader += "</div>";
htmlHeader += "</div>";

// YouTube Playlist Section
htmlHeader += "<div style='width: 50%; overflow-wrap: break-word;'>";
htmlHeader += "<h4 style='margin-bottom: -12px; margin-top: 10px;'>Playlist de Referência:</h4>";
let allVideoIds =[];
for (let index = 0; index < songDatas.length; index++) {
    if (songDatas[index].linkRef) {
        const links = songDatas[index].linkRef.split("|");
        links.forEach(link => {
            let videoId = YouTubeGetID(link);
            if (videoId != null) {
                allVideoIds.push(videoId);
            }
        });
    }
}
// Remove duplicates
let uniqueVideoIds = [...new Set(allVideoIds)];

let playlistLink = `https://www.youtube.com/watch_videos?video_ids=${uniqueVideoIds.join(',')}&start_radio=1`;
htmlHeader += "<div style='display: flex; align-items: center;'>";
htmlHeader += `<img width="100px" style="margin-top: 5px;" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(playlistLink)}">`;
htmlHeader += `<a class="cover-playlist-link" href="${playlistLink}" target="_blank" style="margin-left: 10px;"></a>`;
htmlHeader += "</div>";
htmlHeader += "</div>";

htmlHeader += "</div>";

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
    var jsonResponse = JSON.parse(response);

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
    	toneHtmlContent += ` | <span class="link">REFERÊNCIA: `;
    	songDatas[index].linkRef.split("|").forEach(link =>
    		{
					toneHtmlContent+= `<a href="${link.trim()}" target="_blank"></a></br>`;
    		}
  		)
			toneHtmlContent+= `</span>`;
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

// Ajusta linhas que possuem notação musical
const preElements = document.getElementsByTagName('pre');
const musicalNotations = ['𝅘𝅥','𝅘𝅥𝅮'];

Array.from(preElements).forEach(preElement => {
    const containsNotation = musicalNotations.some(notation =>
        preElement.textContent.includes(notation)
    );

    if (containsNotation) {
        preElement.classList.add('music-notation');
    }
});

// Transformação final do Whatsapp MSG em TXT de texto puro para evitar chamadas de API web
var whats_text = whats_msg.join('\n');
var blob = new Blob([whats_text], { type: 'text/plain;charset=utf-8' });
whats_url = URL.createObjectURL(blob);
console.log("Arquivo de texto gerado para o WhatsApp criado: " + whats_url);

console.log("finalizado!");
window.open(whats_url, '_blank');

// Abrindo a nova guia com o texto para copiar no Whatsapp
setTimeout(function() {
	window.print();
}, 2000);