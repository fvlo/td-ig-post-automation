# Post automatically to Instagram
Script that programatically creates images based on input text and scheduling in google sheets. Posting to Instagram is done using selenium and the latelysocial.com service.  
Deployed with GCP and Docker.

>Will currently not work due to changes to latelysocial's web UI.
>Likely fix is to edit selenium sequence for login page.

https://www.instagram.com/triviadeck/ (the account is not active)  

![What the posts on instagram look like](/example.png)

### How to use
Run igpost_orchestrator. This will read instructions from [gsheets](https://docs.google.com/spreadsheets/d/1b3KojEnGWyRxAz1lMcPjani2SfGRg3nlkDGPglfPxjI/edit#gid=0) and call ig_carousel_via_latelysocial. New sheets should not be added to this gsheets file.

### Docker container
Folder for_docker contains necessary resources for creating docker image.
To build image named td_ig_post_automation: "docker build --tag td_ig_post_automation ."
To run container: "docker run td_ig_post_automation"

Note that docker versions of files are slightly different:
- ig_carousel_via_latelysocial added webdriver options on lines 129 and 130
- igpost_orchestrator is .py and not notebook-format

### Deployed to GCP
*GCP project deleted*
