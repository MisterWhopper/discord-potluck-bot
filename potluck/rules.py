from potluck.models import *
import math

def calc_pl_item_requirements(pl: Potluck):
    """
    As more users accept the invitation to the potluck, more goods
    will be required. Using perfectpotluck[.]com as a guide,
    we can round up to the nearest multiple of 10.

    Additionally, if we know that some users have diet restrictions
    we can adjust the counts (e.g. ensuring a vegan entree is required
    if at least one user is a vegan)
    """
    # A guesstimate of how many people a single item of each type can feed
    # TODO: Make this a configuration item?
    per_person_mapping = {
        ItemType.ENTREE: 10,
        ItemType.SIDE: 5,
        ItemType.BEVERAGE: 15,
        ItemType.DESSERT: 10
    }
    min_item_counts = {k: math.ceil(len(pl.participants) / v) for k,v in per_person_mapping.items()}
    for commitment in pl.item_commitments:
        # TODO: Add diet/allergen checking here
        min_item_counts[commitment.item_type] -= 1
    current_item_counts = {k: v for k,v in min_item_counts.items() if v > 0}
    return current_item_counts

async def on_pl_event_create(event: PLEventCreateEvent, ctx: NotifierCallback):
    if not event.from_user.is_mod:
        await ctx.notifier.send_message(
            ctx.message_factory.build(MessageType.USER_NOT_PERMITTED), event.from_user
        )
        return
    await ctx.repository.save(event.potluck)
    await ctx.notifier.send_announcement(
        ctx.message_factory.build(MessageType.PL_EVENT_CREATED)
    )


async def on_pl_event_edit(event: PLEventEditEvent, ctx: NotifierCallback):
    """
    1. Retrieve the tracking entry
    1a. Verify the user is either a mod or the organizer of the event themselves
    2. Update the details
    3. Save back to repository
    4. Update previously sent message
    """
    potluck = await ctx.repository.try_get_pl_event(event.pl_name)
    if potluck is None:
        await ctx.notifier.send_message(
            ctx.message_factory.build(MessageType.PL_EVENT_NOT_FOUND), event.from_user
        )
    if not (event.from_user == potluck.organizer or event.from_user.is_mod):
        await ctx.notifier.send_message(
            ctx.message_factory.build(MessageType.USER_NOT_PERMITTED), event.from_user
        )
    event.new_potluck.announcement_message.id = potluck.announcement_message.id
    await ctx.repository.remove(potluck)
    await ctx.repository.save(event.new_potluck)
    await ctx.notifier.update_message(
        potluck.announcement_message.id, event.new_potluck
    )


# NOTE: in discy just call this if either the proper scheduled event or the announcement message are deleted
async def on_pl_event_delete(event: PLEventDeleteEvent, ctx: NotifierCallback):
    pass


async def on_pl_event_accept_precheck(event: IEvent, ctx: NotifierCallback):
    """
    1. Check to see if user has already set up a profile
        1a. if not, then maybe we decline the interaction until they do it?
    2. Send user a message prompting them for their contribution
    """
    pass


async def on_pl_event_decline_precheck(event: IEvent, ctx: NotifierCallback):
    pass


async def on_pl_event_accept_postcheck(event: IEvent, ctx: NotifierCallback):
    """
    1. Retrive tracking entry
    2. Add user as a participant
    3. Recalc required items based on contribution
    4. Update health considerations if necessary
    5. Update & save tracking entry
    6. Update announcement message
    """
    pass


async def on_pl_event_decline_postcheck(event: IEvent, ctx: NotifierCallback):
    pass


async def on_pl_profile_edit(event: IEvent, ctx: NotifierCallback):
    """
    1. Check if user ever created a profile (if not, create it)
    2. Update w/ new user parms & save to repo
    """
    pass


def start_pl_bot(
    notifier: INotifier,
    repository: IRepository,
    message_factory: IMessageFactory,
    settings: Optional[AppSettings] = None,
):
    """
    Operations as follows:
        1. Intitialize the repository if necessary
        2. register all event callbacks
        3. pass control to notifier.run()
    """
    if not repository.is_initialized():
        repository.init(settings)
    callback_builder = partial(
        NotifierCallback,
        notifier=notifier,
        repository=repository,
        message_factory=message_factory,
        settings=settings,
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_CREATE, callback_builder(on_pl_event_create)
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_EDIT, callback_builder(on_pl_event_edit)
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_DELETE, callback_builder(on_pl_event_delete)
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_ACCEPT_PRECHECK,
        callback_builder(on_pl_event_accept_precheck),
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_DECLINE_PRECHECK,
        callback_builder(on_pl_event_decline_precheck),
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_ACCEPT_POSTCHECK,
        callback_builder(on_pl_event_accept_postcheck),
    )
    notifier.forward_event_registration(
        EventType.PL_EVENT_DECLINE_POSTCHECK,
        callback_builder(on_pl_event_decline_postcheck),
    )
    notifier.forward_event_registration(
        EventType.PL_PROFILE_EDIT, callback_builder(on_pl_profile_edit)
    )
    notifier.run()
