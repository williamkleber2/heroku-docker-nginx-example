async function showNotification(title, message, options) {
    const permission = await Notification.requestPermission();

    if (permission === "granted") {
        if (message)
            options = { ...options, body: message };

        return new Notification(title, options);
    };
};
