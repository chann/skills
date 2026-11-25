# API design

**You own the contract a caller sees, and every caller who will come to depend on it.**

1. Write the contract before the implementation: the operations, the input and
   output types, the error cases, and what a caller may rely on. A caller
   written from the contract alone must work.
2. Assume everything observable gets depended on: ordering, timing, error
   text, defaults. Decide what is promised, and hide or mark as unstable
   everything else.
3. Give the whole surface one error shape: a stable code a program branches
   on and a message a person reads, with each status meaning the same thing
   everywhere. Validate input where it enters and name the field that failed.
4. Name each concept one way across the surface. A list paginates from its
   first version. An operation a client may retry takes an idempotency key and
   returns the first result for a repeat.
5. Model variants so impossible states do not fit: a tagged union per variant,
   separate input and output types, a distinct type for each kind of id.
6. Change by adding: a new optional field, a new operation. Removing or
   redefining something published is a breaking change; run it under the
   migration playbook.
7. Prove it with a consumer: one real call per operation and per error case,
   and every existing caller still passing. Document the contract in the same
   change.
8. Ship with the shipping playbook.

**Reply:** the contract and where it lives, what is promised and what is marked unstable, each breaking change avoided or declared, and the consumer calls that prove it.
