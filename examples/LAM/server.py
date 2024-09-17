if __name__ == "__main__":
    from polysophia.core import Server, TextPacket

    server = Server(name="sample_server", address="http://127.0.0.1:4567")

    def processor(packet: TextPacket):
        print(f"SERVER: {packet.text}")

    server.respond(processor=processor, inputs=)
