# Tailscale Setup

Cassandra contact points are discovered dynamically at startup via the Tailscale API. For discovery to work, Cassandra
nodes on your tailnet **must carry the correct ACL tags**.

## Required Tags on Cassandra Nodes

| Tag                  | Purpose                                       |
|----------------------|-----------------------------------------------|
| `tag:cassandra-node` | Marks the device as a Cassandra instance      |
| `tag:backend`        | Marks the device as a backend instance        |
| `tag:prod`           | Scopes the node to the production environment |
| `tag:test`           | Scopes the node to the test environment       |

At startup the backend authenticates with the Tailscale API using OAuth credentials, lists all online devices on the
tailnet, and filters for nodes carrying both `tag:cassandra-node` and the environment-matching tag. It then randomly
samples up to **3 contact points** from the viable set, retrying with exponential backoff if discovery fails.

> Tags are configured in your Tailscale ACL policy. Refer to
> the [Tailscale ACL tags documentation](https://tailscale.com/kb/1068/acl-tags) for setup instructions.

## Creating the OAuth Client

In the Tailscale admin console go to **Settings → OAuth Clients**, create a client with `devices:read` scope, and supply
the generated credentials as `TAILSCALE_API_CLIENT_ID` and `TAILSCALE_API_CLIENT_SECRET`.
