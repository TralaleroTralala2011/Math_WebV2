# V43 targeted contrast fix

Only `learning-path.html` gains a scoped stylesheet. Other site pages, backend, database and authentication are unchanged.

For admin access, configure a private secret on Render and use an authenticated password-reset workflow; never embed an unchangeable master password in public source.

Browser and deployment regression testing still required.
