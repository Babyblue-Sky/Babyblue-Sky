// Apps Script, NOT part of the Python pipeline — paste this into a Google
// Slides file's own bound script editor (Extensions > Apps Script), not a
// standalone script.google.com project. It only works there because
// SlidesApp.getActivePresentation() needs a container to bind to.
//
// Prerequisite: the file must already be native Google Slides format, not
// a .pptx opened in Office-compatibility mode (that mode has no Extensions
// menu at all). If Drive shows a yellow ".PPTX" badge next to the filename,
// go File > "Save as Google Slides" first to get a real native copy.
//
// Purpose: notebook_to_pptx.py (see that file's docstring) tags every
// Chinese text run with the font "Kaiti SC" — a macOS-local font Google
// Slides can't read, since Slides runs in the browser with no access to
// local system fonts and only recognizes fonts from its own web font
// library (mostly Google Fonts). This script re-applies a font Slides can
// actually render, to Chinese characters only — English/pinyin/numbers in
// the same text box are left untouched.
//
// One-time setup before running: in Slides, select any Chinese text, open
// the font dropdown > "More fonts", search for the font name below, add it
// to the file. (Font landscape as of 2026-08, see PROJECT_STATUS.md for the
// full writeup — Google Fonts has no true "Kaiti"/STKaiti/华文楷体, that's
// a proprietary OS font. Closest options: "LXGW WenKai TC" (Google's own
// description: brings the clarity/charm of KaiTi style) or "Noto Serif SC"
// (not Kaiti-styled, but a clean formal serif that reads reliably). The
// cursive/brush Google Fonts — Ma Shan Zheng, Zhi Mang Xing, Long Cang, Liu
// Jian Mao Cao — are too hard to read at body-text size for a full deck;
// fine for a one/two-character decorative title, not for lesson content.)

function fixChineseFontOnly() {
  var targetFont = "LXGW WenKai TC";  // must already be added via "More fonts" in this file
  var cjk = /[一-鿿㐀-䶿]/;
  var slides = SlidesApp.getActivePresentation().getSlides();

  slides.forEach(function(slide) {
    slide.getShapes().forEach(function(shape) {
      if (!shape.getText) return;
      var textRange = shape.getText();
      var str = textRange.asString();
      if (!str.length) return;

      var i = 0;
      while (i < str.length) {
        var isCjk = cjk.test(str[i]);
        var j = i + 1;
        while (j < str.length && cjk.test(str[j]) === isCjk) {
          j++;
        }
        if (isCjk) {
          textRange.getRange(i, j).getTextStyle().setFontFamily(targetFont);
        }
        i = j;
      }
    });
  });
}
