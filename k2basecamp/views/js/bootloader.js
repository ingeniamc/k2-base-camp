/**
 * After selecting a firmware with the file dialog, this function updates the interface.
 * The name of the file is displayed and the button used to select a firmware file is disabled.
 * @param {str} firmware 
 * @param {int} drive 
 */
function setFirmware(firmware, drive) {
    switch (drive) {
        case Enums.Drive.Left:
            firmwareFileLeft.text = firmware;
            resetFirmwareLeft.visible = true;
            firmwareButtonLeft.enabled = false;
            break;
        case Enums.Drive.Right:
            firmwareFileRight.text = firmware;
            resetFirmwareRight.visible = true;
            firmwareButtonRight.enabled = false;
    }
}

/**
 * Set the state of the GUI after a scan returned the ids of the drives in the network.
 * @param {int[]} servoIDs 
 */
function setServoIDs(servoIDs) {
    const servoIDsModel = servoIDs.map((servoID) => {
        return {
            value: servoID,
            text: servoID
        }
    });
    idLeftAutomatic.model = servoIDsModel;
    idLeftAutomatic.enabled = true;
    // Handle if the scan returned only one servo
    if (servoIDsModel.length > 1) {
        idRightAutomatic.model = servoIDsModel;
        idRightAutomatic.incrementCurrentIndex();
        idRightAutomatic.enabled = true;
    } else {
        idRightAutomatic.enabled = false;
    }
    idsAutomatic.visible = true;
}

/**
 * Resets the installation dialog.
 */
function resetDialog() {
    progressLeftDialog.visible = false
    progressLeftDialogBar.indeterminate = true;
    progressRightDialog.visible = false
    progressRightDialogBar.indeterminate = true;
    progressDialogButtons.visible = true
    isInProgress.visible = false
    progressDialog.close();
}

/**
 * Updates the progress bar in the GUI when the installation progress gets updated.
 * @param {int[]} drives 
 */
function showInstallationProgress(drives) {
    progressDialogButtons.visible = false
    isInProgress.visible = true
    for (const drive of drives) {
        switch (drive) {
            case Enums.Drive.Left:
                progressLeftDialog.visible = true
                break;
            case Enums.Drive.Right:
                progressRightDialog.visible = true
                break;
        }
    }
}