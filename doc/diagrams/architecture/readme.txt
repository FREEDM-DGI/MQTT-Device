On MQTT Architecture Tom Says:

I've attached what I believe represents the architecture that NCSU has developed for MQTT after looking through their code and documentation.

On Ideal MQTT Architecture Tom Says:

And here is my understanding of the ideal MQTT architecture for DGI, under the assumptions that the DGI is not the broker and there is no plug-and-play.

It requires greater code effort to make the DGI the broker, and NCSU has not implemented a MQTT plug-and-play that tolerates crash failures, leading to both assumptions.
