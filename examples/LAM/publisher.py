if __name__ == "__main__":
    from polysophia.core import Publisher, TextPacket

    publisher = Publisher(name="sample_publisher", address="http://127.0.0.1:4567")

    def processor(packet: TextPacket):
        print(f"PUBLISHER: {packet.text}")

    publisher.publish(processor=processor, inputs=)
