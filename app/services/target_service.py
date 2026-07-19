from app.services.bounty_hunter import find_bounty_targets


def get_targets():

    targets = find_bounty_targets(20)

    return targets
