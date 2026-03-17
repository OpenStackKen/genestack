---
title: "Object Store Management using the Skyline GUI"
weight: 180
aliases:
  - /storage-object-store-skyline-gui/
---
## Goal

Use the `Skyline` GUI to perform operations on your object store.

## Prerequisites

Ensure you have access to your OpenStack Skyline GUI.

## Documentation

### Create an object container

Create the container named "flex-container01":

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, you can now click Create Container.

![Skyline GUI NAV](/assets/images/storage-object-store-skyline-gui-01-navigate.png)

- Enter the name for your container in the resulting dialog box. Please note that the container name cannot be changed once created. If you need a different name, you'll need to create another container. If you'd like the container to be made Public, you can switch the slider on here.

![Skyline GUI NAV](/assets/images/storage-object-store-skyline-gui-02-create-dialog.png)

- Click OK.

![Skyline GUI NAV](/assets/images/storage-object-store-skyline-gui-03-container-list.png)

If you'd like to make the container public after it's created:

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, under the Action heading, click Update.
- Switch the slider on or off here.
- Click OK.

View the container's detail:

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, under the Detail Info heading, click Detail Info.
- Click somewhere else on the page to dismiss the Detail Info box.

### Upload a file to the container

Upload a file to the container:

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, under the Name heading, click on your container's name.
- Click Upload File

![Skyline GUI NAV](/assets/images/storage-object-store-skyline-gui-04-in-container.png)

- Using your file chooser, navigate and select a file.
- Click OK. Depending on the size of your file, you may see a progress bar, while your file is uploaded.

![Skyline GUI NAV](/assets/images/storage-object-store-skyline-gui-05-file-list.png)

> [!NOTE]
>
>
> Note that at this time, the Skyline GUI cannot upload entire folders.
>

To accomplish this you can use either the [openstack client](/cloud-onboarding/storage-object-store-openstack-cli/) or the [swift client](/cloud-onboarding/storage-object-store-swift-cli/).

### Downloading files
When the container is public, you can access each file using a specific URL, made up of your region's endpoint, the name of your container, the prefix (if any) of your object, and finally, the object name.
``` shell
<REGIONAL_ENDPOINT>/storage/container/detail/flex-container01/example.rtf
```

Download a single file from the container:

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, under the Name heading, click on your container's name.
- Locate the file you wish to download.
- On the far right, click More, then Download File.
- Click Confirm.

### Deleting objects

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, under the Name heading, click on your container's name.
- Locate the file you wish to delete.
- Click Delete.
- Click Confirm.

### Deleting a containers

- Navigate to Storage > Object Storage using the left-hand menu.
- Using the right-hand section, locate the container you wish to delete.
- Click Delete.
- Click Confirm.

> [!NOTE]
>
>
> Note that at this time, the Skyline GUI cannot delete non-empty containers.
>

To accomplish this you can use either the [openstack client](/cloud-onboarding/storage-object-store-openstack-cli/) or the [swift client](/cloud-onboarding/storage-object-store-swift-cli/).

### Setting and removing object expiration
At this time, setting and removing object expiration can be done using the the [swift client](/cloud-onboarding/storage-object-store-swift-cli/).

## Additional documentation

Additional documentation can be found at the official skyline site, on the Openstack Documentation Site.\
https://wiki.openstack.org/wiki/Skyline
