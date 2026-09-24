---
title: "Asynchrouns and Transactional Event Listeners in Spring"
date: 2017-10-06T23:53:00.003+02:00
updated: 2017-10-06T23:55:16.702+02:00
author: "Rafał Borowiec"
tags: ["spring"]
original_url: https://blog.codeleak.pl/2017/10/asynchrouns-and-transactional-event.html
---

# Asynchrouns and Transactional Event Listeners in Spring

The built-in event publication functionality exists from the early Spring versions and it is still useful for handling basic communication between Spring components in the same application context. In general, the application can generate application events (that can be arbitrary objects) and listen to them. The whole mechanism is really simple: using `ApplicationPublisher` you publish events and using `EventListener` you handle them. What I find especially useful is *asynchronous and transactional event listeners*.

One of the example where events can be used is when a component wants to signal that an **entity** (in terms of JPA) was created or modified so that other interested components (listeners) can react to this event and trigger some business logic (e.g. schedule a notification). Usually such code is executed within a Spring managed transaction. For example:

```
@Service
public class TaskService {

    private static final Logger LOG = LoggerFactory.getLogger(TaskService.class);

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    public Task createTask(String name) {

        Task task = new Task();
        task.setName(name);
        task.setCreated(LocalDateTime.now());

        LOG.info("Publishing task created event: {}", task);

        eventPublisher.publishEvent(new TaskCreatedEvent(task));

        try {
            return taskRepository.save(task);
        } finally {
            LOG.info("Event published. Saving task: {}", task);
        }
    }
}
```

The above service publishes an event with task instance before it was actually saved. Handling such events can be done in several ways in Spring. To demonstrate what happens with the task instance I will check its state with JPA `EntityManager`:

- if is it transient (no id was set),
- if it is managed by entity manager or
- if it detached (not transient, not managed but exists).

Let’s look at the listener:

```
@Service
public class TaskCreatedEventListener {

    private static final Logger LOG = LoggerFactory.getLogger(TaskCreatedEventListener.class);

    @Resource
    EntityManager entityManager;

    // @Async
    // @EventListener
    // @TransactionalEventListener
    public void handleEvent(TaskCreatedEvent taskCreatedEvent) throws InterruptedException {
        Task task = taskCreatedEvent.getTask();
        LOG.info("Is task transient? {}", isTransient(task));
        LOG.info("Is task managed? {}", isManaged(task));
        LOG.info("Is task detached? {}", isDetached(task));
    }

    private boolean isTransient(Task task) {
        return task.getId() == null;
    }

    private boolean isManaged(Task task) {
        return entityManager.contains(task);
    }

    private boolean isDetached(Task task) {
        return !isTransient(task)
            && !isManaged(task)
            && exists(task);
    }

    private boolean exists(Task task) {
        return entityManager.find(Task.class, task.getId()) != null;
    }

}
```

Let’s go through several examples. What would be the behavior if we have:

- `@EventListener`

This is standard listener that is invoked synchronously. The method will be executed before transaction is complete hence the object will be in **transient** state.

- `@Async @EventListener`

Adding `@Async` to `@EventListener` will make the method is executed asynchronously hence in different thread (don’t forget to enable asynchronous method execution in the application). In our scenario **most likely** the object with be in **transient** state but in real life it can be also **detached** as the the publisher could save the task already. So in fact, the behavior is not deterministic.

- `@TransactionalEventListener`

When the listener is marked as transactional event listener, Spring publishes the event to listener only when the publisher was called in the boundaries of the transaction and its *after commit* phase (this can be adjusted through the annotation). In such scenario, the object will be in **managed** state.

- `@Async @TransactionalEventListener`

This is the most interesting case. As above, Spring publishes the event to listener only when the publisher was called in the boundaries of the transaction and its *after commit* phase, but the transaction finishes so the object is in the **detached** state - there is a different transaction running.
