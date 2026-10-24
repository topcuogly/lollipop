import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const created = [];
let removed = false;
function Panel() {
 this.widgets = [];
 this.addWidget = function(type) {
  const w = { type, settings: {}, writeConfig(key, value) { this.settings[key] = value; } };
  this.widgets.push(w);
  return w;
 };
 created.push(this);
}
const file = new URL('../profile/airootfs/usr/share/lollipop/layout.js', import.meta.url);
let output = '';
vm.runInNewContext(fs.readFileSync(file, 'utf8'), { Panel, desktops: () => [], panels: () => [{ remove() { removed = true; } }], print: text => { output += text; } });
assert.equal(output, 'LOLLIPOP_LAYOUT_OK');
assert.ok(removed);
assert.equal(created.length, 2);
const [top, dock] = created;
assert.equal(top.location, 'top');
assert.equal(top.height, 28);
assert.equal(top.lengthMode, 'fill');
assert.equal(top.floating, true);
assert.equal(top.widgets[0].type, 'org.kde.plasma.activitybar');
assert.equal(top.widgets.filter(w => w.type === 'org.kde.plasma.digitalclock').length, 1);
assert.equal(dock.location, 'right');
assert.equal(dock.height, 64);
assert.equal(dock.alignment, 'right');
assert.equal(dock.hiding, 'dodgewindows');
assert.equal(dock.lengthMode, 'fit');
assert.equal(dock.floating, true);
assert.equal(dock.widgets.length, 2);
assert.equal(dock.widgets[0].type, 'org.kde.plasma.icontasks');
assert.equal(dock.widgets[0].settings.reverseMode, true);
assert.ok(!JSON.stringify(created).includes('firefox'));
console.log('PASS: layout script execution and panel/widget contract (mock API; no visual/runtime acceptance)');

assert.equal(dock.widgets[1].type, 'org.kde.plasma.kickoff');
assert.equal(dock.widgets[1].settings.icon, 'lollipop-launcher');

assert.deepEqual(Array.from(dock.widgets[0].settings.launchers), ["applications:virt-manager.desktop", "applications:org.kde.dolphin.desktop", "applications:app.zen_browser.zen.desktop", "applications:dev.zed.Zed.desktop", "applications:org.libreoffice.LibreOffice.desktop"]);

// Plain desktops need a widget, Folder View needs only the prepared desktop file.
for (const live of [false, true]) {
 const icons = [];
 const desktops = ['org.kde.desktopcontainment', 'org.kde.plasma.folder'].map(type => ({
  type, writeConfig() {}, addWidget(type, ...geometry) {
   const widget = {type, geometry, settings: {}, writeConfig(key, value) {this.settings[key] = value;}};
   icons.push(widget); return widget;
  }
 }));
 vm.runInNewContext(fs.readFileSync(file, 'utf8'), {Panel, lollipopLive: live, desktops: () => desktops, panels: () => [], print() {}});
 assert.equal(icons.length, live ? 1 : 0);
 if (live) assert.equal(icons[0].settings.url, 'file:///usr/share/applications/install-lollipop.desktop');
}
