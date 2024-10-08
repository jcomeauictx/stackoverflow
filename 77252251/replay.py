'''
https://docs.mitmproxy.org/stable/addons-examples/#duplicate-modify-replay
'''

from mitmproxy import ctx

def request(flow):
    """
    Take incoming HTTP requests and replay them with modified parameters.
    """
    # Avoid an infinite loop by not replaying already replayed requests
    if flow.is_replay == "request":
        return
    flow = flow.copy()
    # Only interactive tools have a view. If we have one, add a duplicate entry
    # for our flow.
    if "view" in ctx.master.addons:
        ctx.master.commands.call("view.flows.duplicate", [flow])
    flow.request.path = "/changed"
    ctx.master.commands.call("replay.client", [flow])
