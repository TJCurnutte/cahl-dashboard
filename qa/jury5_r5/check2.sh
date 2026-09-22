#!/bin/bash
cd /Users/traviscurnutte/cahl-dashboard/qa/jury5_r5
echo '--- A. "tonight" user-facing renders in app.js ---'
grep -n "tonight" app_v55.js | grep -vi '^\s*[0-9]*:\s*//' | grep -v ':[0-9]*: *//' | head -10
echo '--- B. JS_VERSION / APP_VERSION ---'
grep -n "JS_VERSION\|APP_VERSION" app_v55.js | head -6
grep -n "APP_VERSION\|data-version\|window\." index_v55.html | grep -i version | head -5
echo '--- C. Saira weights in index.html fonts href ---'
grep -o "family=Saira[^&\"]*" index_v55.html
echo '--- CSS font-weight: 800 users ---'
grep -n "Saira" style_v55.css | head -5
grep -c "font-weight: *800\|font-weight:800" style_v55.css
echo '--- D. placeholder/raw-render tells in app.js ---'
grep -n "\[object\|undefined<\|>undefined\|NaN\|null<" app_v55.js | head -10
echo '--- E. verBadge/vBadge legacy ---'
grep -in "badge" index_v55.html | head -5
grep -in "badge" app_v55.js | head -5
echo '--- F. autoToggle checked-state feedback CSS ---'
grep -n "autoToggle\|auto-toggle\|input:checked" style_v55.css | head -8
grep -n "autoToggle" app_v55.js | head -5
