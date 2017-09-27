# LFP Scheduler

This is a django app that helps us schedule LFP appointments for clients. It uses the microsoft graph rest api to send event creation requests to outlook with the parameters from the form.

Eventually we will want to extend this to be capable of being public-facing.

### todo

- [ ] Query to see if a timeslot is filled before creating a new appointment
- [ ] Add metrics
- [ ] Better client and serverside security and sanitation
- [ ] Find a way for users without LFP calendar access to still send requests
