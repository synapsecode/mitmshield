# MITMShield
This project is a man-in-the-middle proxy server that investigates if outbound requests contain any sensitive / confidential information and blocks it right away

## TODOs / Future Roadmap
- [ ] Create a source bucket (this is a central repository of all the code/strings on the system that are marked as confidential)
- [ ] Add support for detection in HTTPs encrypted sending using MITM's internal SSL cert
- [ ] Support the form-data POST upload alternative (google gemini etc)
- [ ] Add Support for Email outbound detection (HARD)
- [ ] Add Support for Telegram, Whatsapp and other messengers (HARD)
- [ ] Snoop into WebSocket data also
- [ ] Include a Systemwide Clipboard watchdog that sprinkles watermarks into copied content (if it is confidential), watermarks are stripped if pasted into supported-apps