********
Examples
********

This page contains guides that outline examples of how to extend the existing code with new functionality.

It is meant to be a starting point for developing your own application that has all the features you need.

Changing the value of a register
================================

One of the main functions of the program is that it allows you to communicate with the drive using the `ingenialink <https://distext.ingeniamc.com/doc/ingenialink-python/latest/>`_ library.

The objective of this example is changing the value of a register of the drive upon changing the content of an input box in the GUI.

#.  Add the input box to the frontend::

        SpinBox {
            (component properties)
            onValueModified: () => {
                grid.connectionController.set_register_max_velocity(value, Enums.Drive.Left);
            }
        }

    As we can see, the box defines a handler that triggers when the value changes. We use it to call a function of ``connectionController``.
    However, in order for this to work, we need the ``connectionController`` to be accessible in the frontend.

#.  Add the ``connectionController`` as a property in our **main.qml**::

        ApplicationWindow {
            id: page
            title: qsTr("K2 Base Camp")
            required property ConnectionController connectionController
            ...        
        }

#.  Making a ``controller`` accessible in qml happens in **__main__.py**::

        ...
        qml_file = os.fspath(Path(__file__).resolve().parent / "views/main.qml")
        engine = QQmlApplicationEngine()

        drive_controller = ConnectionController()
        engine.setInitialProperties({"connectionController": drive_controller})

        engine.load(qml_file)
        ...

#.  If the ``SpinBox`` is a direct child component of **main.qml**, we can continue with the next step. However, since we have separated our code over several pages, we need to pass the ``connectionController`` to the ``ControlsPage``, which holds the ``SpinBox``::

        ApplicationWindow {
            ...

            ControlsPage {
                id: controlsPage
                connectionController: page.connectionController
            }
        }

#.  Now we can implement the function in the ``ConnectionController``::

        @Slot(float, int)
        def set_register_max_velocity(self, max_velocity: float, drive: int) -> None:
            self.mcs.run(
                self.log_report,
                "communication.set_register",
                "CL_VEL_REF_MAX",
                max_velocity,
                Drive(drive).name,
            )

    Note the ``@Slot`` decorator - it is necessary for the function to be callable from the GUI and defines the types of the parameters it expects.
    We are making use of the ``MotionControllerService`` here, calling its "run" function with several parameters. 
    This is the most basic way to communicate with the drive and allows us to directly invoke a single `ingenialink <https://distext.ingeniamc.com/doc/ingenialink-python/latest/>`_ function.
    That function (in this case ``communication.set_register``) will be executed **in a seperate thread** with all parameters that come after it (``max_velocity``, ``Drive(drive).name``).
    Upon conclusion, the callback function (``self.log_report``) will be invoked.
    The ``thread`` we use to communicate with the drive is an instance of ``MotionControllerThread``, which was created when ``MotionControllerService`` was instantiated.

#.  The callback function can be used to update the frontend with data returned from the ``thread`` (it is passed to the callback as a ``thread_report``). However, in this case we simply log the result to the console::

        def log_report(self, report: thread_report) -> None:
            logger.debug(report)


More complex communication with the drive
=========================================

Oftentimes, calling a single `ingenialink <https://distext.ingeniamc.com/doc/ingenialink-python/latest/>`_ function is not enough. 
For example, when enabling the motor, we need to set the operation mode before calling the ``motor_enable`` function.
``MotionControllerService`` provides the ``@run_on_thread`` utility decorator for these use cases. 
Essentially, it allows us to define a function that is passed in its entirety to the ``MotionControllerThread`` and executed there "in one go".

We will assume that the ``controller`` we want to use is already connected to QML (see previous example for details).

#.  Define a checkbox to enable the motor in the GUI::

        CheckBox {
            id: motorEnable
            text: qsTr("Enable motor")
            onToggled: () => {
                if (motorEnable.checked) {
                    grid.connectionController.enable_motor(Enums.Drive.Left);
                } else {
                    ...
                }
            }
        }

#.  In the ``connectionController``, define the corresponding function::

        @Slot(int)
        def enable_motor(self, drive: int) -> None:
            target = Drive(drive)
            if target == Drive.Left:
                self.mcs.enable_motor(self.enable_motor_l_callback, target)
            else:
                self.mcs.enable_motor(self.enable_motor_r_callback, target)

#.  As we can see, this time we call a custom function in the ``MotionControllerService``. We need to write it ourselves::

        @run_on_thread
        def enable_motor(
            self,
            report_callback: Callable[[thread_report], Any],
            drive: Drive,
            *args: Any,
            **kwargs: Any,
        ) -> Callable[..., Any]:
            def on_thread(drive: Drive) -> Any:
                self.__mc.motion.set_operation_mode(
                    OperationMode.PROFILE_VELOCITY, servo=drive.name
                )
                self.__mc.motion.motor_enable(servo=drive.name)

            return on_thread

    Note that the ``@run_on_thread`` decorator needs to be included in the function header.

    .. WARNING::
        
        Everything except the ``drive: Drive`` argument of both functions (``enable_motor`` and ``on_thread``), as well as the content of the ``on_thread`` - function is boilerplate.

Polling
=======

Since we just enabled a motor, we might want to continuosly monitor one of the drives registers (in this case the current motor velocity).
Looking at the previous example, we might notice that the ``connectionController`` indicated a callback function to be executed when the ``MotionControllerThread`` finished its task.

#.  Let's use this callback function to start an instance of ``PollerThread`` to carry out the monitoring task::

        def enable_motor_l_callback(self, thread_report: thread_report) -> None:
            poller_thread = self.mcs.create_poller_thread(
                Drive.Left.name, [{"name": "CL_VEL_FBK_VALUE", "axis": 1}]
            )
            poller_thread.new_data_available_triggered.connect(
                self.handle_new_velocity_data_l
            )
            poller_thread.start()

    The actual creation of the new ``thread`` is handled in the ``MotionControllerService`` (see the ``create_poller_thread`` function for details), but the important thing to highlight here is the following line::

        poller_thread.new_data_available_triggered.connect(
                self.handle_new_velocity_data_l
            )

#.  ``PollerThread`` defines a ``signal`` (``new_data_available_triggered``) which will emit when it receives new data from the drive. With the code above, we connect this ``signal`` to a function defined in ``ConnectionController``::

        @Slot()
        def handle_new_velocity_data_l(
            self, timestamps: list[float], data: list[list[float]]
        ) -> None:
            self.velocity_left_changed.emit(timestamps[0], data[0][0])

    The function by itself does not do too much (it refactors the incoming data), but crucially it triggers the ``velocity_left_changed`` ``signal`` (also defined in ``ConnectionController``) to emit the data that was received (Drive -> ``PollerThread`` -> ``ConnectionController``).

#.  ``Signals`` coming from a ``controller`` can be received in the GUI, which allows us to plot the data there::

        RowLayout {
            id: grid
            required property ConnectionController connectionController

            Connections {
                target: grid.connectionController
                function onVelocity_left_changed(timestamp, velocity) {
                    PlotJS.updatePlot(chartL, timestamp, velocity);
                }
                (more signal handlers..)
        }
    
    The ``connectionController`` property is the same as outlined in the first example. 
    The important part to look at here is the `Connections - component <https://doc.qt.io/qt-6/qml-qtqml-connections.html>`_.
    It defines a target to connect to - this is where ``signals`` are coming from.
    It then defines handlers that will trigger when a specific ``signal`` is emitted.
    The name of the function corresponds to the ``signal`` we wish to react to, prefixed with an "on" (``onVelocity_left_changed`` fires when ``velocity_left_changed`` emits).
    We now have the data available in the GUI and can draw a plot (refer to the ``updatePlot`` - javascript function for details).


Writing tests
=============

In order to write tests for the application, you can make use of all the great features of pytest (e.g. `fixtures <https://docs.pytest.org/en/6.2.x/fixture.html>`_).
The ``tests`` folder includes examples for both ``unit`` and ``gui`` tests.
The ``gui`` tests make use of the ``qtbot`` fixture (provided by *pytest-qt*) and the ``mocker`` fixture (provided by *pytest-mock*).