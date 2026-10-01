document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupCsrfProtection();
        setupTheme();
        setupSidebar();
        setupSettingsPanel();
        setupNotificationsPanel();
        setupSidebarSubscriptions();
        setupVideoReactions();
        setupCommentReactions();
        setupSubscriptions();
        setupWatchLater();
        setupDescriptionToggle();
        setupServerToasts();
        setupUploadValidation();

    }
);


function getCookie(name) {

    if (!document.cookie) {
        return null;
    }

    const cookies =
        document.cookie.split(";");

    for (const cookie of cookies) {

        const trimmed =
            cookie.trim();

        if (
            trimmed.startsWith(
                `${name}=`
            )
        ) {

            return decodeURIComponent(
                trimmed.substring(
                    name.length + 1
                )
            );
        }
    }

    return null;
}


function getCsrfToken() {

    const cookieToken =
        getCookie("csrftoken");

    if (cookieToken) {
        return cookieToken;
    }

    const csrfInput =
        document.querySelector(
            "input[name='csrfmiddlewaretoken']"
        );

    return csrfInput
        ? csrfInput.value
        : null;
}


function setupCsrfProtection() {

    document.addEventListener(
        "submit",
        function (event) {

            const form =
                event.target;

            if (
                !(form instanceof HTMLFormElement)
            ) {
                return;
            }

            const method =
                (
                    form.getAttribute("method")
                    || "get"
                ).toLowerCase();

            if (method !== "post") {
                return;
            }

            const csrfInput =
                form.querySelector(
                    "input[name='csrfmiddlewaretoken']"
                );

            const currentToken =
                getCookie("csrftoken");

            if (
                csrfInput
                && currentToken
            ) {
                csrfInput.value =
                    currentToken;
            }
        },
        true
    );
}


function setupVideoReactions() {

    const likeButton =
        document.querySelector("#like-button");

    const dislikeButton =
        document.querySelector("#dislike-button");


    if (!likeButton || !dislikeButton) {
        return;
    }


    let requestPending = false;


    likeButton.addEventListener(
        "click",
        async function () {

            if (requestPending) {
                return;
            }

            requestPending = true;

            disableVideoReactions(
                true
            );

            const videoId =
                likeButton.dataset.videoId;

            try {

                const data =
                    await sendReactionRequest(
                        `/video/${videoId}/like/`
                    );

                if (!data) {
                    return;
                }

                updateVideoReactions(
                    data
                );

            } finally {

                requestPending = false;

                disableVideoReactions(
                    false
                );
            }

        }
    );


    dislikeButton.addEventListener(
        "click",
        async function () {

            if (requestPending) {
                return;
            }

            requestPending = true;

            disableVideoReactions(
                true
            );

            const videoId =
                dislikeButton.dataset.videoId;

            try {

                const data =
                    await sendReactionRequest(
                        `/video/${videoId}/dislike/`
                    );

                if (!data) {
                    return;
                }

                updateVideoReactions(
                    data
                );

            } finally {

                requestPending = false;

                disableVideoReactions(
                    false
                );
            }

        }
    );
}


function disableVideoReactions(disabled) {

    const likeButton =
        document.querySelector(
            "#like-button"
        );

    const dislikeButton =
        document.querySelector(
            "#dislike-button"
        );

    if (likeButton) {
        likeButton.disabled = disabled;
    }

    if (dislikeButton) {
        dislikeButton.disabled = disabled;
    }
}


function updateVideoReactions(data) {

    const likeButton =
        document.querySelector(
            "#like-button"
        );

    const dislikeButton =
        document.querySelector(
            "#dislike-button"
        );

    const likeCount =
        document.querySelector(
            "#like-count"
        );

    const dislikeCount =
        document.querySelector(
            "#dislike-count"
        );


    likeButton.classList.toggle(
        "active",
        data.liked
    );

    dislikeButton.classList.toggle(
        "active",
        data.disliked
    );


    likeCount.textContent =
        data.like_count;

    dislikeCount.textContent =
        data.dislike_count;
}


function setupCommentReactions() {

    const likeButtons =
        document.querySelectorAll(
            ".comment-like-button"
        );


    const dislikeButtons =
        document.querySelectorAll(
            ".comment-dislike-button"
        );


    likeButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                async function () {

                    const comment =
                        button.closest(
                            ".comment"
                        );

                    if (
                        comment.dataset
                            .reactionPending === "true"
                    ) {
                        return;
                    }

                    comment.dataset.reactionPending =
                        "true";


                    setCommentButtonsDisabled(
                        comment,
                        true
                    );


                    const commentId =
                        button.dataset.commentId;


                    try {

                        const data =
                            await sendReactionRequest(
                                `/comment/${commentId}/like/`
                            );


                        if (!data) {
                            return;
                        }


                        updateCommentReactions(
                            comment,
                            data
                        );

                    } finally {

                        comment.dataset.reactionPending =
                            "false";


                        setCommentButtonsDisabled(
                            comment,
                            false
                        );
                    }

                }
            );

        }
    );


    dislikeButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                async function () {

                    const comment =
                        button.closest(
                            ".comment"
                        );


                    if (
                        comment.dataset
                            .reactionPending === "true"
                    ) {
                        return;
                    }


                    comment.dataset.reactionPending =
                        "true";


                    setCommentButtonsDisabled(
                        comment,
                        true
                    );


                    const commentId =
                        button.dataset.commentId;


                    try {

                        const data =
                            await sendReactionRequest(
                                `/comment/${commentId}/dislike/`
                            );


                        if (!data) {
                            return;
                        }


                        updateCommentReactions(
                            comment,
                            data
                        );

                    } finally {

                        comment.dataset.reactionPending =
                            "false";


                        setCommentButtonsDisabled(
                            comment,
                            false
                        );
                    }

                }
            );

        }
    );
}


function setCommentButtonsDisabled(
    comment,
    disabled
) {

    const buttons =
        comment.querySelectorAll(
            ".comment-like-button, .comment-dislike-button"
        );

    buttons.forEach(
        function (button) {

            button.disabled =
                disabled;

        }
    );
}


function updateCommentReactions(
    comment,
    data
) {

    const likeButton =
        comment.querySelector(
            ".comment-like-button"
        );

    const dislikeButton =
        comment.querySelector(
            ".comment-dislike-button"
        );

    const likeCount =
        comment.querySelector(
            ".comment-like-count"
        );

    const dislikeCount =
        comment.querySelector(
            ".comment-dislike-count"
        );


    likeButton.classList.toggle(
        "active",
        data.liked
    );

    dislikeButton.classList.toggle(
        "active",
        data.disliked
    );


    likeCount.textContent =
        data.like_count;

    dislikeCount.textContent =
        data.dislike_count;
}


async function getFreshCsrfToken() {

    try {

        const response =
            await fetch(
                "/csrf-token/",
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store"
                }
            );

        if (!response.ok) {
            return null;
        }

        const data =
            await response.json();

        return data.csrfToken || null;

    } catch (error) {

        console.error(
            "Erro ao atualizar token CSRF:",
            error
        );

        return null;
    }
}


async function sendReactionRequest(url) {

    async function makeRequest(token) {

        return await fetch(
            url,
            {
                method: "POST",

                headers: {
                    "X-CSRFToken": token,
                    "X-Requested-With": "XMLHttpRequest"
                },

                credentials: "same-origin"
            }
        );
    }


    let csrfToken =
        getCsrfToken();


    if (!csrfToken) {

        csrfToken =
            await getFreshCsrfToken();
    }


    if (!csrfToken) {

        console.error(
            "Token CSRF não encontrado."
        );

        return null;
    }


    try {

        let response =
            await makeRequest(
                csrfToken
            );


        if (response.status === 403) {

            const freshToken =
                await getFreshCsrfToken();


            if (!freshToken) {

                console.error(
                    "Não foi possível atualizar o token CSRF."
                );

                return null;
            }


            response =
                await makeRequest(
                    freshToken
                );
        }


        if (!response.ok) {

            console.error(
                "Erro na reação:",
                response.status
            );

            return null;
        }


        return await response.json();

    } catch (error) {

        console.error(
            "Erro ao enviar reação:",
            error
        );

        return null;
    }
}

function setupSubscriptions() {

    const subscribeButtons =
        document.querySelectorAll(
            ".subscribe-button"
        );


    subscribeButtons.forEach(
        function (button) {

            let requestPending = false;


            button.addEventListener(
                "click",
                async function () {

                    if (requestPending) {
                        return;
                    }


                    const csrfToken =
                        getCsrfToken();


                    if (!csrfToken) {

                        console.error(
                            "Token CSRF não encontrado."
                        );

                        return;
                    }


                    requestPending = true;
                    button.disabled = true;


                    const username =
                        button.dataset.channel;


                    try {

                        const response =
                            await fetch(
                                `/channel/${username}/subscribe/`,
                                {
                                    method: "POST",

                                    headers: {
                                        "X-CSRFToken":
                                            csrfToken,

                                        "X-Requested-With":
                                            "XMLHttpRequest"
                                    },

                                    credentials:
                                        "same-origin"
                                }
                            );


                        if (!response.ok) {

                            console.error(
                                "Erro ao alterar inscrição:",
                                response.status
                            );

                            return;
                        }


                        const data =
                            await response.json();


                        const text =
                            button.querySelector(
                                ".subscribe-text"
                            );


                        if (data.subscribed) {

                            button.classList.add(
                                "subscribed"
                            );

                            text.textContent =
                                "Inscrito";

                        } else {

                            button.classList.remove(
                                "subscribed"
                            );

                            text.textContent =
                                "Inscrever-se";
                        }


                        showToast(
                            data.subscribed
                                ? "Inscrição realizada."
                                : "Inscrição removida.",
                            "success"
                        );


                        const channelCount =
                            document.querySelector(
                                "#channel-subscriber-count"
                            );


                        const watchCount =
                            document.querySelector(
                                "#watch-subscriber-count"
                            );


                        if (channelCount) {

                            channelCount.textContent =
                                data.subscriber_count;
                        }


                        if (watchCount) {

                            watchCount.textContent =
                                data.subscriber_count;
                        }

                    } catch (error) {

                        console.error(
                            "Erro ao alterar inscrição:",
                            error
                        );

                    } finally {

                        requestPending = false;
                        button.disabled = false;
                    }

                }
            );

        }
    );
}


/* =========================
   NOSVID UI / THEME
========================= */

function resolveTheme(preference) {

    if (preference === "system") {

        return window.matchMedia(
            "(prefers-color-scheme: dark)"
        ).matches
            ? "dark"
            : "light";
    }

    return preference;
}


function applyTheme(preference) {

    const safePreference = [
        "light",
        "dark",
        "system"
    ].includes(preference)
        ? preference
        : "system";

    const resolvedTheme =
        resolveTheme(safePreference);

    document.documentElement.dataset.theme =
        resolvedTheme;

    document.documentElement.dataset.themePreference =
        safePreference;

    localStorage.setItem(
        "nosvid-theme",
        safePreference
    );

    document
        .querySelectorAll(".theme-option")
        .forEach(function (button) {

            const selected =
                button.dataset.themeChoice
                === safePreference;

            button.classList.toggle(
                "active",
                selected
            );

            button.setAttribute(
                "aria-checked",
                selected ? "true" : "false"
            );
        });
}


function setupTheme() {

    const savedTheme =
        localStorage.getItem(
            "nosvid-theme"
        ) || "system";

    applyTheme(savedTheme);

    const mediaQuery =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        );

    mediaQuery.addEventListener(
        "change",
        function () {

            const currentPreference =
                localStorage.getItem(
                    "nosvid-theme"
                ) || "system";

            if (
                currentPreference === "system"
            ) {
                applyTheme("system");
            }
        }
    );

    document
        .querySelectorAll(".theme-option")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    applyTheme(
                        button.dataset.themeChoice
                    );
                }
            );
        });
}


function setupSidebar() {

    const toggleButton =
        document.querySelector(
            "#sidebar-toggle"
        );

    const backdrop =
        document.querySelector(
            "#sidebar-backdrop"
        );

    if (!toggleButton) {
        return;
    }

    const desktopMedia =
        window.matchMedia(
            "(min-width: 901px)"
        );

    const savedCollapsed =
        localStorage.getItem(
            "nosvid-sidebar-collapsed"
        ) === "true";

    if (
        desktopMedia.matches
        && savedCollapsed
    ) {

        document.body.classList.add(
            "sidebar-collapsed"
        );

        toggleButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    function closeMobileSidebar() {

        document.body.classList.remove(
            "sidebar-mobile-open"
        );
    }


    toggleButton.addEventListener(
        "click",
        function () {

            if (desktopMedia.matches) {

                document.body.classList.toggle(
                    "sidebar-collapsed"
                );

                const collapsed =
                    document.body.classList.contains(
                        "sidebar-collapsed"
                    );

                localStorage.setItem(
                    "nosvid-sidebar-collapsed",
                    collapsed
                        ? "true"
                        : "false"
                );

                toggleButton.setAttribute(
                    "aria-expanded",
                    collapsed
                        ? "false"
                        : "true"
                );

            } else {

                document.body.classList.toggle(
                    "sidebar-mobile-open"
                );
            }
        }
    );


    if (backdrop) {

        backdrop.addEventListener(
            "click",
            closeMobileSidebar
        );
    }


    document
        .querySelectorAll(
            ".sidebar-item[href]"
        )
        .forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    if (
                        !desktopMedia.matches
                    ) {
                        closeMobileSidebar();
                    }
                }
            );
        });


    desktopMedia.addEventListener(
        "change",
        function (event) {

            closeMobileSidebar();

            if (event.matches) {

                const collapsed =
                    localStorage.getItem(
                        "nosvid-sidebar-collapsed"
                    ) === "true";

                document.body.classList.toggle(
                    "sidebar-collapsed",
                    collapsed
                );

                toggleButton.setAttribute(
                    "aria-expanded",
                    collapsed
                        ? "false"
                        : "true"
                );

            } else {

                document.body.classList.remove(
                    "sidebar-collapsed"
                );

                toggleButton.setAttribute(
                    "aria-expanded",
                    "true"
                );
            }
        }
    );
}


function setupSettingsPanel() {

    const openButton =
        document.querySelector(
            "#settings-open"
        );

    const closeButton =
        document.querySelector(
            "#settings-close"
        );

    const panel =
        document.querySelector(
            "#settings-panel"
        );

    const backdrop =
        document.querySelector(
            "#settings-backdrop"
        );

    if (
        !openButton
        || !panel
        || !backdrop
    ) {
        return;
    }


    function openSettings() {

        document.body.classList.add(
            "settings-open"
        );

        panel.setAttribute(
            "aria-hidden",
            "false"
        );

        backdrop.setAttribute(
            "aria-hidden",
            "false"
        );
    }


    function closeSettings() {

        document.body.classList.remove(
            "settings-open"
        );

        panel.setAttribute(
            "aria-hidden",
            "true"
        );

        backdrop.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    openButton.addEventListener(
        "click",
        openSettings
    );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeSettings
        );
    }


    backdrop.addEventListener(
        "click",
        closeSettings
    );


    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {
                closeSettings();
            }
        }
    );
}

/* =========================
   WATCH LATER
========================= */

function setupWatchLater() {

    const button =
        document.querySelector(
            "#watch-later-button"
        );

    if (!button) {
        return;
    }

    let requestPending = false;


    button.addEventListener(
        "click",
        async function () {

            if (requestPending) {
                return;
            }


            const csrfToken =
                getCsrfToken();


            if (!csrfToken) {

                console.error(
                    "Token CSRF não encontrado."
                );

                return;
            }


            requestPending = true;
            button.disabled = true;


            const videoId =
                button.dataset.videoId;


            try {

                const response =
                    await fetch(
                        `/video/${videoId}/watch-later/`,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    csrfToken,

                                "X-Requested-With":
                                    "XMLHttpRequest"
                            },

                            credentials:
                                "same-origin"
                        }
                    );


                if (!response.ok) {

                    console.error(
                        "Erro ao alterar Assistir mais tarde:",
                        response.status
                    );

                    return;
                }


                const data =
                    await response.json();


                const text =
                    document.querySelector(
                        "#watch-later-text"
                    );


                button.classList.toggle(
                    "active",
                    data.saved
                );


                if (text) {

                    text.textContent =
                        data.saved
                            ? "Salvo"
                            : "Assistir mais tarde";
                }

                showToast(
                    data.saved
                        ? "Vídeo salvo para assistir mais tarde."
                        : "Vídeo removido de Assistir mais tarde.",
                    "success"
                );

            } catch (error) {

                console.error(
                    "Erro ao alterar Assistir mais tarde:",
                    error
                );

            } finally {

                requestPending = false;
                button.disabled = false;
            }

        }
    );
}


/* =========================
   VIDEO DESCRIPTION
========================= */

function setupDescriptionToggle() {

    const description =
        document.querySelector(
            "#video-description"
        );

    const text =
        document.querySelector(
            "#video-description-text"
        );

    const button =
        document.querySelector(
            "#description-toggle"
        );

    if (
        !description
        || !text
        || !button
    ) {
        return;
    }

    requestAnimationFrame(
        function () {

            const needsToggle =
                text.scrollHeight
                > text.clientHeight + 4;

            if (!needsToggle) {
                button.hidden = true;
                description.classList.add(
                    "description-short"
                );
            }
        }
    );

    button.addEventListener(
        "click",
        function () {

            const expanded =
                description.classList.toggle(
                    "expanded"
                );

            button.textContent =
                expanded
                    ? "Mostrar menos"
                    : "Mostrar mais";

            button.setAttribute(
                "aria-expanded",
                expanded
                    ? "true"
                    : "false"
            );
        }
    );
}


/* =========================
   TOASTS / FEEDBACK
========================= */

function setupServerToasts() {

    document
        .querySelectorAll(
            ".server-toast"
        )
        .forEach(
            function (toast) {

                const message =
                    toast.dataset.toastMessage
                    || toast.textContent.trim();

                let type = "success";

                if (
                    toast.classList.contains("error")
                    || toast.classList.contains("warning")
                ) {
                    type = "error";
                }

                toast.remove();

                showToast(
                    message,
                    type
                );
            }
        );
}


function showToast(
    message,
    type = "success"
) {

    let container =
        document.querySelector(
            "#toast-container"
        );

    if (!container) {

        container =
            document.createElement(
                "div"
            );

        container.id =
            "toast-container";

        container.className =
            "toast-container";

        container.setAttribute(
            "aria-live",
            "polite"
        );

        container.setAttribute(
            "aria-atomic",
            "true"
        );

        document.body.appendChild(
            container
        );
    }

    const toast =
        document.createElement(
            "div"
        );

    toast.className =
        `nosvid-toast ${type}`;

    const icon =
        type === "error"
            ? "!"
            : "✓";

    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message"></span>
    `;

    const messageElement =
        toast.querySelector(
            ".toast-message"
        );

    messageElement.textContent =
        message;

    container.appendChild(
        toast
    );

    requestAnimationFrame(
        function () {

            toast.classList.add(
                "show"
            );
        }
    );

    const removeToast =
        function () {

            toast.classList.remove(
                "show"
            );

            window.setTimeout(
                function () {
                    toast.remove();
                },
                220
            );
        };

    window.setTimeout(
        removeToast,
        3200
    );

    toast.addEventListener(
        "click",
        removeToast
    );
}


function setupUploadValidation() {

    const videoInput =
        document.querySelector("#video_file");

    const thumbnailInput =
        document.querySelector("#thumbnail");

    const uploadForm =
        (
            videoInput
            && videoInput.closest("form")
        )
        || (
            thumbnailInput
            && thumbnailInput.closest("form")
        );


    const maxVideoSize =
        100 * 1024 * 1024;

    const maxThumbnailSize =
        5 * 1024 * 1024;


    function validateFile(
        input,
        maxSize,
        message
    ) {

        if (
            !input
            || !input.files
            || !input.files.length
        ) {
            return true;
        }

        const file =
            input.files[0];

        if (file.size > maxSize) {

            showToast(
                message,
                "error"
            );

            input.value = "";

            return false;
        }

        return true;
    }


    if (videoInput) {

        videoInput.addEventListener(
            "change",
            function () {

                validateFile(
                    videoInput,
                    maxVideoSize,
                    "O vídeo deve ter no máximo 100 MB."
                );
            }
        );
    }


    if (thumbnailInput) {

        thumbnailInput.addEventListener(
            "change",
            function () {

                validateFile(
                    thumbnailInput,
                    maxThumbnailSize,
                    "A thumbnail deve ter no máximo 5 MB."
                );
            }
        );
    }


    if (uploadForm) {

        uploadForm.addEventListener(
            "submit",
            function (event) {

                const videoValid =
                    validateFile(
                        videoInput,
                        maxVideoSize,
                        "O vídeo deve ter no máximo 100 MB."
                    );

                const thumbnailValid =
                    validateFile(
                        thumbnailInput,
                        maxThumbnailSize,
                        "A thumbnail deve ter no máximo 5 MB."
                    );

                if (
                    !videoValid
                    || !thumbnailValid
                ) {
                    event.preventDefault();
                }
            }
        );
    }
}


/* =========================
   NOTIFICATIONS PANEL
========================= */

function setupNotificationsPanel() {

    const openButton =
        document.querySelector(
            "#notifications-open"
        );

    const closeButton =
        document.querySelector(
            "#notifications-close"
        );

    const panel =
        document.querySelector(
            "#notifications-panel"
        );

    const backdrop =
        document.querySelector(
            "#notifications-backdrop"
        );

    const markAllButton =
        document.querySelector(
            "#notifications-mark-all"
        );


    if (
        !openButton
        || !panel
        || !backdrop
    ) {
        return;
    }


    function openPanel() {

        panel.classList.add(
            "open"
        );

        backdrop.classList.add(
            "visible"
        );

        panel.setAttribute(
            "aria-hidden",
            "false"
        );

        backdrop.setAttribute(
            "aria-hidden",
            "false"
        );

        openButton.setAttribute(
            "aria-expanded",
            "true"
        );

        document.body.classList.add(
            "notifications-open"
        );

    }


    function closePanel() {

        panel.classList.remove(
            "open"
        );

        backdrop.classList.remove(
            "visible"
        );

        panel.setAttribute(
            "aria-hidden",
            "true"
        );

        backdrop.setAttribute(
            "aria-hidden",
            "true"
        );

        openButton.setAttribute(
            "aria-expanded",
            "false"
        );

        document.body.classList.remove(
            "notifications-open"
        );
    }


    openButton.addEventListener(
        "click",
        function () {

            if (
                panel.classList.contains(
                    "open"
                )
            ) {
                closePanel();
            } else {
                openPanel();
            }
        }
    );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closePanel
        );
    }


    backdrop.addEventListener(
        "click",
        closePanel
    );

    if (markAllButton) {
        markAllButton.addEventListener(
            "click",
            async function () {
                await markNotificationsAsRead();
                markAllButton.disabled = true;
            }
        );
    }


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape"
                && panel.classList.contains(
                    "open"
                )
            ) {
                closePanel();
            }
        }
    );
}


async function markNotificationsAsRead() {

    const badge =
        document.querySelector(
            "#notification-badge"
        );

    const unreadItems =
        document.querySelectorAll(
            ".notification-popup-item.unread"
        );


    if (
        !badge
        && unreadItems.length === 0
    ) {
        return;
    }


    const csrfToken =
        getCsrfToken();


    if (!csrfToken) {
        return;
    }


    try {

        const response =
            await fetch(
                "/notifications/read/",
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            csrfToken,

                        "X-Requested-With":
                            "XMLHttpRequest"
                    },

                    credentials:
                        "same-origin"
                }
            );


        if (!response.ok) {
            return;
        }


        if (badge) {
            badge.remove();
        }


        const markAllButton =
            document.querySelector(
                "#notifications-mark-all"
            );

        if (markAllButton) {
            markAllButton.disabled = true;
        }

        unreadItems.forEach(
            function (item) {

                item.classList.remove(
                    "unread"
                );

                const dot =
                    item.querySelector(
                        ".notification-unread-dot"
                    );

                if (dot) {
                    dot.remove();
                }
            }
        );

    } catch (error) {

        console.error(
            "Erro ao marcar notificações como lidas:",
            error
        );
    }
}


/* =========================
   SIDEBAR SUBSCRIPTIONS
========================= */

function setupSidebarSubscriptions() {

    const toggle =
        document.querySelector(
            "#sidebar-subscriptions-toggle"
        );

    const extra =
        document.querySelector(
            "#sidebar-subscriptions-extra"
        );


    if (
        !toggle
        || !extra
    ) {
        return;
    }


    const text =
        toggle.querySelector(
            ".sidebar-show-more-text"
        );

    const icon =
        toggle.querySelector(
            ".sidebar-show-more-icon"
        );


    toggle.addEventListener(
        "click",
        function () {

            const expanded =
                toggle.getAttribute(
                    "aria-expanded"
                ) === "true";


            toggle.setAttribute(
                "aria-expanded",
                expanded
                    ? "false"
                    : "true"
            );

            extra.hidden =
                expanded;


            if (text) {

                text.textContent =
                    expanded
                        ? "Mostrar mais"
                        : "Mostrar menos";
            }


            if (icon) {

                icon.textContent =
                    expanded
                        ? "⌄"
                        : "⌃";
            }
        }
    );
}
