Music Bingo Generator
----------------------

## Requirements
* ffmeg
* wkhtmltopdf

## Python libs
see requirements.txt

## Running
Two methods of auth are included, you may find some tracks do not have a preview_url unless you use `promt_for_auth`
`cc_auth` is usually fine if you already have the tracks. You will need to set the variables in `config.ini`

To generate a set of bingo cards, simply call the `run` method with the id of the spotify playlist. 
You can optionally specify a method/lambda to alter how the track names are displayed.
Included is a crude formatter to strip the track titles back to the bare minimum.

## Number bingo
I thought it would be a fun idea to have a 'regular' bingo game where the card is just numbers and the 
songs played contain the numbers to mark off. For this purpose, `number_decoder` does some crude conversions of numeric words 
into numbers which can then be extracted and displayed instead of the song title.

### Config
`TRACKS_PER_SHEET` - sets the number of tracks on a bingo card  
`NUMBER_OF_SHEETS` - the number of sheets to generate


