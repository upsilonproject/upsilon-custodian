from upsilon import amqp

class AmqpConnection(amqp.Connection):
    def newChannel(self):
        print "overiding new channel"

        channel = self.conn.channel();
        channel.queue_declare(queue = self.queue, durable = False, auto_delete = False)

        return channel

