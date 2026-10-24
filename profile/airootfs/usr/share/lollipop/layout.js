// Plasma 6.8 scripting API. This script is for a fresh Live home only.
// Plasma 6.8 panelview.cpp maps AlignRight to AnchorBottom for vertical panels.
var screens = desktops();
for (var n = 0; n < screens.length; ++n) {
    screens[n].currentConfigGroup = ["General"];
    screens[n].writeConfig("url", "desktop:/");
    // Folder View shows the executable desktop file prepared before SDDM.
    // A plain desktop needs an explicit Icon widget instead.
    if (typeof lollipopLive !== "undefined" && lollipopLive && screens[n].type !== "org.kde.plasma.folder") {
        var installer = screens[n].addWidget("org.kde.plasma.icon", 24, 48, 112, 112);
        installer.currentConfigGroup = ["General"];
        installer.writeConfig("url", "file:///usr/share/applications/install-lollipop.desktop");
    }
}
var previous = panels();
for (var i = 0; i < previous.length; ++i) previous[i].remove();
var top = new Panel;
top.location = "top";
top.height = 28;
top.lengthMode = "fill";
top.floating = true;
top.hiding = "none";
top.opacity = "translucent";
top.addWidget("org.kde.plasma.activitybar");
var leftSpacer = top.addWidget("org.kde.plasma.panelspacer");
leftSpacer.currentConfigGroup = ["General"];
leftSpacer.writeConfig("expanding", true);
var clock = top.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd d MMM");
clock.writeConfig("dateDisplayFormat", 1);
clock.writeConfig("use24hFormat", 2);
var rightSpacer = top.addWidget("org.kde.plasma.panelspacer");
rightSpacer.currentConfigGroup = ["General"];
rightSpacer.writeConfig("expanding", true);
var tray = top.addWidget("org.kde.plasma.systemtray");
tray.currentConfigGroup = ["General"];
tray.writeConfig("hiddenItems", ["org.kde.plasma.battery"]);
var battery = top.addWidget("org.kde.plasma.battery");
battery.currentConfigGroup = ["General"];
battery.writeConfig("showPercentage", true);
var dock = new Panel;
dock.location = "right";
dock.height = 64;
dock.lengthMode = "fit";
dock.alignment = "right";
dock.offset = 12; // Provisional spacing, pending visual acceptance.
dock.floating = true;
dock.hiding = "dodgewindows";
dock.opacity = "translucent";
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", ["applications:virt-manager.desktop", "applications:org.kde.dolphin.desktop", "applications:app.zen_browser.zen.desktop", "applications:dev.zed.Zed.desktop", "applications:org.libreoffice.LibreOffice.desktop"]);
tasks.writeConfig("reverseMode", true);
tasks.writeConfig("separateLaunchers", true);
tasks.writeConfig("fill", false);
tasks.writeConfig("showOnlyCurrentActivity", true);
var apps = dock.addWidget("org.kde.plasma.kickoff");
apps.currentConfigGroup = ["General"];
apps.writeConfig("icon", "lollipop-launcher");
print("LOLLIPOP_LAYOUT_OK");
