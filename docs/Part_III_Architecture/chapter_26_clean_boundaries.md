# Chapter 26: Clean Boundaries

## Boundaries

We seldom control all the software in our systems. Sometimes we buy third-party packages or use open source. Other times we depend on teams in our own company to produce components or subsystems. Somehow we must integrate this foreign code cleanly. This chapter looks at practices and techniques for keeping software boundaries clean.

## Third-Party IoT Framework: Lots of Boundaries

The example system automates testing of a high-capacity water pump. A technician traditionally measures water pressure at several nozzles and records the readings manually. Given the geometry of the nozzles, pressure is converted into flow rate. A test can take 20 to 30 minutes and wastes a lot of water.

The first design used Bluetooth to communicate from an electronic pressure sensor to a tablet or smartphone. It worked in the lab, but brick walls blocked the signal in the field. An Internet-of-Things infrastructure could carry the measurements through those walls.

We selected an IoT vendor whose infrastructure allowed us to build the application in Python. We expected that we might need a different vendor when the product went to market because cost, vendor viability, or the rapidly changing IoT market could change. We wanted to preserve our investment in business logic, so the prototype needed clean code, separation of concerns, and limited dependence on the vendor infrastructure.

The vendor provided a simple “hello world” application. We turned that example into a layer containing the vendor dependencies. We used only the small portion of the vendor’s broad interface needed for message passing. The project was code-named Hydra.

The `HydraNetwork` class encapsulates the hub’s dependencies on the IoT vendor. Its functions are low-complexity delegates to the communications infrastructure. During initialization, the hub announces itself to listening radios and polls the framework for replies.

```python
class HydraNetwork:
    def announce_hub(self):
        self.broadcast('announceHub', '')
        self.poll_a_second()

    def process_ack(self, command, payload):
        sensor_id = self.source_addr()
        self.ack_handler.handle_reply(sensor_id, command, payload)
```

The radio remembers the hub address and sends an acknowledgment:

```python
def announce_hub():
    global hub_addr
    hub_addr = rpc_source_addr()
    info = node_identity()
    send_ack(hub_addr, 'announceHub', info)
```

The acknowledgment handler is an injected dependency, an instance of `HydraDataSource`. It passes received bookkeeping and payloads to other parts of the Hydra system. There is no application work to do for an `announceHub` acknowledgment.

`HydraDataSource` initiates a network read once per second during a flow test. Each update has a synchronization token so asynchronous measurement replies can be grouped by second. When a new second starts, a report is saved for the previous second.

```python
class HydraDataSource:
    def flow_update(self):
        self.sync_token.next()
        self.network.broadcast(
            'initiateRead',
            self.sync_token.value()
        )
        self.report = self.reply_dispatcher.report()
```

When `initiateRead` is broadcast, each radio replies asynchronously. The radio sends an acknowledgment and asks a separate microcontroller for the latest analog-to-digital-converter measurement.

```python
def initiate_read(sync_token):
    global hub_addr
    hub_addr = rpc_source_addr()
    send_ack(hub_addr, 'initiateRead', sync_token)
    report_measurement(sync_token)


def report_measurement(sync_token):
    print('RA ' + sync_token)


def measurement_done(reply):
    if not valid_serial_reply(reply):
        reply = 'Error: invalid serial reply'
    send_ack(hub_addr, 'SensorReply', reply[:MAX_SIZE])
```

When the measurement is ready, the ADC microcontroller sends a CSV string over the serial connection. The radio sends it as a `SensorReply` acknowledgment. The hub dispatches that message to the application. The reply dispatcher knows the CSV format and where to send the parsed data. It and its collaborators are test-driven and free from IoT dependencies.

```python
class HydraDataSource:
    def handle_reply(self, sensor_id, command, payload):
        sync_token = self.sync_token.value

        if command == 'SensorReply':
            self.reply_dispatcher.sensor_update(
                sensor_id,
                sync_token,
                payload
            )
```

Because `HydraNetwork` encapsulates the IoT framework dependencies, a different vendor’s infrastructure can be substituted without changing the Hydra core application.

## UI/Application Boundary

The user interface is a Web browser on a tablet or smartphone. The application uses a Web-server framework, but the business logic is separated from it. The application runs as two processes on a small Linux computer:

- The Collector process gathers measurements from `HydraNetwork`.
- The WebServer process runs the Web server in its main thread.

The user’s start and stop commands reach the Collector through a `CommandQueue`. Measurement updates are sent to a `ReplyQueue` after a synchronized group of measurements is collected.

The Collector waits on the command queue with a one-second timeout. Each timeout initiates a refresh and flow update.

```python
def measurement_loop(command_q, reply_q, command_runner, update_interval):
    command = None

    while command != HYDRA_EXIT:
        command = get_message(command_q, update_interval)

        if command is None:
            command = HYDRA_REFRESH

        reply = command_runner.run(command)
        put_message(reply_q, reply)
```

The entry point receives its data source as an injected dependency. Production uses `HydraDataSource`; development and testing can use a simulated data source that does not need a network.

```python
def hydra_run(port, data_source, polling_rate, logger):
    logger.info('Hydra start')

    command_runner = CommandRunner(data_source, logger)
    collector = Process(
        target=measurement_loop,
        args=(command_q, reply_q, command_runner, polling_rate)
    )
    collector.start()

    sleep(1)
    logger.info('Hydra collector started')
    run_hydra_web_server(port, command_q, reply_q)
    logger.info('Hydra web server exited')

    command_q.put(HYDRA_EXIT)
    collector.join()
    logger.info('Hydra shut down')
```

All dependencies come together at this entry point. The code is not complex and is unlikely to change often.

Important boundary attributes include:

- Business logic is free from knowledge of the radio system.
- IoT-dependent functions are low-complexity and unlikely to change often.
- Business logic is separate from the UI.
- Communication between the application and Web server uses simple queues.
- Business logic is not concerned with concurrency.
- Concurrency mechanisms are isolated in low-complexity functions.
- Object creation is separate from object use.
- During initialization, concrete objects are created and bound to processes and to each other.
- Binding is based on a need-to-know basis.

## SOLID and Hexagonal Architecture

Following the SOLID principles and isolating dependencies on the outside world naturally leads to hexagonal architecture, also called Ports and Adapters.

Inside the hexagon is the product’s logic and behavior. Responsibilities are allocated to separate classes, functions, and domain objects rather than one large ball of mud. Outside the hexagon is the execution environment. The application depends on service-abstraction layers at the edge of the hexagon.

The UI drives the system through the `CommandQueue`. A start command travels to the sensors, which begin collecting measurements. `CommandRunner` waits for UI commands, and each one-second timeout initiates another sensor update. The previous second’s readings are bundled into a report and sent to the `ReplyQueue`.

`HydraNetwork` encapsulates the IoT vendor framework. Its `broadcast` operation tells sensors to report their measurements, and its `handle_reply` operation feeds sensor messages into the Hydra application. Hydra knows nothing about the vendor. The interfaces are shaped around what the Hydra application needs, not around everything the vendor offers.

If a new vendor does not provide broadcast, its `HydraNetwork` adapter can address each sensor individually. The adapter may become more complex, but the vendor can be changed without touching the Hydra core.

## Exploring and Learning Boundaries

Third-party code helps us deliver functionality quickly, but learning and integrating it at the same time is difficult. Instead of experimenting directly in production code, write tests that explore the third-party API. These are learning tests: controlled experiments that check our understanding of the API.

For example, before using Python queues in production, we can test the behavior of the message functions:

```python
class QueueLearningTest(unittest.TestCase):
    def test_get_message_returns_message(self):
        queue = Queue(maxsize=1)
        self.assertTrue(put_message(queue, 'hey'))
        self.assertEqual('hey', get_message(queue, 1.0))

    def test_get_message_returns_none_after_timeout(self):
        queue = Queue(maxsize=1)
        self.assertIsNone(get_message(queue, 0.01))

    def test_put_message_returns_false_when_full(self):
        queue = Queue(maxsize=1)
        self.assertTrue(put_message(queue, 'hey1'))
        self.assertFalse(put_message(queue, 'hey2'))
```

We can also learn how queues behave across processes:


Learning tests are precise experiments that improve understanding. When a third-party package is updated, they can reveal behavioral differences immediately. Once integrated, third-party code is not guaranteed to remain compatible with our needs. Boundary tests reduce the risk of migration and make it easier to move away from old versions.

## Using Code That Does Not Yet Exist

Another kind of boundary separates the known from the unknown. Sometimes the other side is unknowable for now, or we choose not to look beyond it.

Suppose a radio-communications system has a `Transmitter` subsystem whose hardware and API have not yet been defined. We can define the interface we wish we had instead of blocking work on the unknown subsystem:

```python
class Transmitter:
    def transmit(self, frequency, data_stream):
        raise NotImplementedError
```

The application-specific interface remains under our control. Client code stays readable and focused on its purpose instead of being burdened by implementation details. Once the real transmitter API is defined, a `TransmitterAdapter` can bridge the gap. The adapter provides a single place to change as the API evolves.

This design also creates a convenient seam for testing. A `FakeTransmitter` can be used to test communication controllers, while boundary tests can verify that the adapter uses the real transmitter API correctly.

## Clean Boundaries

Interesting things happen at boundaries, including change. Good software designs accommodate change without huge investments and rework. When we use code outside our control, we must protect our investment and prevent future changes from becoming costly.

Code at a boundary needs clear separation and tests that define expectations. Avoid allowing much of the application to know about third-party particulars. It is better to depend on something you control than on something you do not control.

Manage third-party boundaries by keeping the number of references to the dependency small. Wrap the dependency in an adapter that converts between the application-centered interface and the provided interface. This keeps usage internally consistent, provides a small number of maintenance points, and makes third-party changes less disruptive.
