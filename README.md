# Movie Maker — AI Narration Studio

A mobile-friendly script-to-audio workspace for Hindi and Hinglish YouTube narration.

## Included
- Single-page narration studio (index.html).
- ElevenLabs API integration for highly natural multilingual Hindi/Hinglish speech.
- Local Edge TTS neural-voice generator (no API key needed).
- Panchayat Season 5 sample script and source notes.
- GitHub Actions workflow that generates a downloadable sample MP3 artifact.

## Open the studio
In GitHub, open Settings → Pages. Under Build and deployment, choose GitHub Actions. GitHub will display the Pages URL when deployment is enabled. You can also download index.html and use it in a modern browser; the sample loader works best on GitHub Pages.

## Highest realism: ElevenLabs
1. Create an API key in your own ElevenLabs account.
2. Enter it in the studio, load voices and select a Hindi-capable Indian male voice.
3. Paste a script and generate the MP3.

The key is kept in this browser tab's session storage and sent directly from your browser to ElevenLabs. It is never committed to this repository or sent to a Movie Maker backend. The default model is Eleven Multilingual v2.

ElevenLabs currently lists a Free plan with a limited monthly character allowance; Free usage is non-commercial and requires attribution. Paid plans provide commercial usage rights. Confirm the current terms before using audio in monetised content.
Pricing: https://elevenlabs.io/pricing
Hindi TTS: https://elevenlabs.io/text-to-speech

## No-key local generator
Install Python 3.10+ and FFmpeg, then run:
    python -m pip install -r requirements.txt
    python generate_edge_audio.py --input scripts/panchayat-season-5-hinglish.txt

The output is audio/Panchayat_Season_5_Hinglish_Narration.mp3. This fallback uses hi-IN-MadhurNeural through the Edge TTS community package. It is a draft/preview route, not a contracted Azure Speech deployment. Check underlying service terms before monetising.

## GitHub Actions
A push changing the sample script or workflow starts an audio build. When complete, open Actions → the latest run → Artifacts, and download panchayat-season5-narration.

## Safety and rights
- Use only voices you have permission to use. Do not clone a real person's voice without consent.
- Never commit API keys or credentials.
- TTS usage rights do not grant rights to movie footage, music, posters or other source material.
- Check YouTube's current disclosure rules for realistic synthetic content.


## Download the built audio from GitHub

The narration workflow commits its MP3 output into:
`audio/Panchayat_Season_5_Hinglish_Narration.mp3`

Open that file in the repository and use **Download raw file** (or open the raw URL and save the audio). The workflow also uploads the same build as a temporary artifact under Actions.
