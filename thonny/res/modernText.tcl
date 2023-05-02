  namespace eval ::modernText {

  # Some parts of this code are copied with modifications from lib/tk8.5/text.tcl which is
  # Copyright (c) 1992-1994 The Regents of the University of California.
  # Copyright (c) 1994-1997 Sun Microsystems, Inc.
  # Copyright (c) 1998 by Scriptics Corporation.

  # Any part of this file that is not copied from lib/tk8.5/text.tcl is Copyright (c) 2005 K. J. Nash and 
  # other contributors to https://wiki.tcl-lang.org/14918
  # You are hereby granted a permanent and irrevocable license to use modify and redistribute this file subject
  # to the terms of the TCL LICENSE AGREEMENT - see https://www.tcl-lang.org/software/tcltk/license.html for
  # further information and note in particular the DISCLAIMER OF ALL WARRANTIES.
  # All other rights reserved.

  if {[catch {package require Tk 8.5}]} {
     puts "Package modernText requires Tk 8.5 or above."
     puts "When obtaining 8.5, note that Tk Version 8.5a4 has a bug (#1333951) in its text widget."
     puts "Please do not use Tcl/Tk 8.5a4 unless you are sure the bug has been fixed."
     exit 1
  }

  if {$::tk_patchLevel eq "8.5a4"} {
   puts "Tk Version 8.5a4 has a bug (#1333951) in its text widget."
   puts "Please do not use Tcl/Tk 8.5a4 unless you are sure the bug has been fixed."
   exit 1
  }

                                     #  Set variables to 1 for "Tk text default" style, 0 for "modern" style
  variable mouseSelectIgnoresKbd 0  ;#  Whether Shift-Button-1 ignores changes made by the kbd to the insert mark
  variable variableAnchor        0  ;#  Whether Shift-Button-1 has a variable or fixed anchor

  variable bCount 0

  ### Two new functions, homeIndex and nameIndex, that can be used for "smart" Home and End operations

  proc homeIndex {w index} {
     # Return the index to jump to (from $index) as "Smart Home"
     # Some corner cases (e.g. lots of leading whitespace, wrapped around) probably have a better solution; but
     # there's no consensus on how a text editor should behave in such cases.

     set index   [$w index $index]
     set dls     [$w index "$index display linestart"]

     # Set firstNonSpace to the index of the first non-space character on the logical line.
     set dlsList [split $dls .]
     set dlsLine [lindex $dlsList 0]
     set lls     $dlsLine.0
     set firstNonSpace [$w search -regexp -- {[^[:space:]]} $dlsLine.0 [expr {$dlsLine + 1}].0]

     # Now massage $firstNonSpace so it contains the "usual" home position on the first display line
     if {$firstNonSpace eq {}} {
        # No non-whitespace characters on the line
        set firstNonSpace $dlsLine.0
     } elseif {[$w count -displaylines $lls $firstNonSpace] != 0} {
        # Either lots of whitespace, or whitespace with character wrap forces $firstNonSpace onto the next
        # display line
        set firstNonSpace $dlsLine.0
     } else {
        # The usual case: the first non-whitespace $firstNonSpace is on the first display line
     }

     if {$dls eq $lls} {
        # We're on the first display line
        if {$index eq $firstNonSpace} {
           # we're at the first non-whitespace of the first display line
           set home $lls
        } else {
           # we're on the first display line, but not at the first non-whitespace
           set home $firstNonSpace
        }
     } else {
        if {$dls eq $index} {
           # we're at the start of a display line other than the first
           set home $firstNonSpace
        } else {
           # we're not on the first display line, and we're not at our display line's start
           set home $dls
        }
     }
     return $home
  }

  proc endIndex {w index} {
     # Return the index to jump to (from $index) as "Smart End"
     set index    [$w index $index]
     set dle      [$w index "$index display lineend"]

     if {$dle eq $index} {
         # we're at the end of a display line: return the logical line end
         return [$w index "$index lineend"]
     } else {
         # return the display line end
         return $dle
     }
  }

  # Make sure that each function we want to copy and modify is loaded - probably unnecessary
  foreach function {
      ::tk_textPaste
      ::tk::TextPasteSelection
      ::tk::TextButton1
      ::tk::TextSelectTo
      ::tk::TextAutoScan
  } {catch $function}

  ### A new function, ::modernText::modernPaste, to replace ::tk_textPaste in bindings - to switch off the
  ### code that makes it behave differently in X11 from other windowing systems.  X11 desktops such as KDE
  ### and GNOME made this change years ago - making the Tk defaults appear anachronistic.

  proc modernPaste w [string map {x11 x11TheOldFashionedWay} [info body ::tk_textPaste]]

  ### Two procs that are copied from ::tk with modifications:

  ### Modify TextClosestGap to fix the jump-to-next-line issue
  ### Modify TextSelectTo to prevent word selection from crossing a line end

  proc TextClosestGap {w x y} {
      # Modified from function ::tk::TextClosestGap
      set pos [$w index @$x,$y]
      set bbox [$w bbox $pos]
      if {$bbox eq ""} {
          return $pos
      }
      if {($x - [lindex $bbox 0]) < ([lindex $bbox 2]/2)} {
          return $pos
      }
      # Never return a position that will place the cursor on the next display line.
      # This used to happen if $x is closer to the end of the display line than to its last character.
      if {[$w cget -wrap] eq "word"} {
          set lineType displaylines
      } else {
          set lineType lines
      }
      if {[$w count -$lineType $pos "$pos + 1 char"] != 0} {
      return $pos
      } else {
      }
      $w index "$pos + 1 char"
  }


  proc TextSelectTo {w x y {extend 0}} {
      # Modified from function ::tk::TextSelectTo
      global tcl_platform
      variable ::tk::Priv

      set cur [TextClosestGap $w $x $y]
      if {[catch {$w index tk::anchor$w}]} {
          $w mark set tk::anchor$w $cur
      }
      set anchor [$w index tk::anchor$w]
      if {[$w compare $cur != $anchor] || (abs($Priv(pressX) - $x) >= 3)} {
          set Priv(mouseMoved) 1
      }
      switch -- $Priv(selectMode) {
          char {
              if {[$w compare $cur < tk::anchor$w]} {
                  set first $cur
                  set last tk::anchor$w
              } else {
                  set first tk::anchor$w
                  set last $cur
              }
          }
          word {
              # Set initial range based only on the anchor (1 char min width - MOD - unless this straddles a
              # display line end)
          if {[$w cget -wrap] eq "word"} {
              set lineType displaylines
          } else {
              set lineType lines
          }
              if {[$w mark gravity tk::anchor$w] eq "right"} {
                  set first "tk::anchor$w"
                  set last "tk::anchor$w + 1c"
                  if {[$w count -$lineType $first $last] != 0} {
                          set last $first
                  } else {
                  }
              } else {
                  set first "tk::anchor$w - 1c"
                  set last "tk::anchor$w"
                  if {[$w count -$lineType $first $last] != 0} {
                          set first $last
                  } else {
                  }
              }
          if {$last eq $first && [$w index $first] eq $cur} {
              # Use $first and $last as above; further extension will straddle a display line.
              # Better to have no selection than a bad one.
          } else {
              # Extend range (if necessary) based on the current point
              if {[$w compare $cur < $first]} {
                  set first $cur
              } elseif {[$w compare $cur > $last]} {
                  set last $cur
              }

              # Now find word boundaries
              set first1 [$w index "$first + 1c"]
              set last1  [$w index "$last - 1c"]
                  if {[$w count -$lineType $first $first1] != 0} {
                          set first1 [$w index $first]
                  } else {
                  }
                  if {[$w count -$lineType $last $last1] != 0} {
                          set last1 [$w index $last]
                  } else {
                  }
              set first2 [::tk::TextPrevPos $w "$first1" tcl_wordBreakBefore]
              set last2  [::tk::TextNextPos $w "$last1"  tcl_wordBreakAfter]
              # Don't allow a "word" to straddle a display line boundary (or, in -wrap char mode, a logical line
              # boundary). Not the right result if -wrap word has been forced into -wrap char because a word is
              # too long.
              # tcl_wordBreakBefore and tcl_wordBreakAfter need fixing too.
              if {[$w count -$lineType $first2 $first] != 0} {
                  set first [$w index "$first display linestart"]
              } else {
                  set first $first2
              }
              if {[$w count -$lineType $last2 $last] != 0} {
                  set last [$w index "$last display lineend"]
              } else {
                  set last $last2
              }
          }
          }
          line {
              # Set initial range based only on the anchor
              set first "tk::anchor$w linestart"
              set last "tk::anchor$w lineend"

              # Extend range (if necessary) based on the current point
              if {[$w compare $cur < $first]} {
                  set first "$cur linestart"
              } elseif {[$w compare $cur > $last]} {
                  set last "$cur lineend"
              }
              set first [$w index $first]
              set last [$w index "$last + 1c"]
          }
      }
      if {$Priv(mouseMoved) || ($Priv(selectMode) ne "char")} {
          $w tag remove sel 0.0 end
          $w mark set insert $cur
          $w tag add sel $first $last
          $w tag remove sel $last end
          update idletasks
      }
  }

  ### (a) The procs in ::tk that we have copied to ::modernText and modified (above) are called directly or 
  ###     indirectly by several procs in ::tk.  Copy and modify these procs too, so that a widget of class
  ###     modernText always uses the ::modernText procs defined above, even if they are called from other procs.

  ### The copy-and-modify code below will likely break when the ::tk code is revised - but this technique makes
  ### the ::modernText code short, and shows exactly what has changed.

  proc TextPasteSelection {w x y} [info body ::tk::TextPasteSelection]

  proc TextButton1 {w x y} [info body ::tk::TextButton1]

  proc TextAutoScan {w}  [string map {tk::TextAutoScan modernText::TextAutoScan} [info body ::tk::TextAutoScan]]


  ### (b) Now make sure that widgets of class modernText always bind to the ::modernText procs defined above
  ### The ::tk namespace, ::tk_textPaste, and the Text binding tag remain in their pristine state.

  ### modernText procs replace these functions - all except ::tk::TextClosestGap occur in bindings
  #    ::tk_textPaste
  #    ::tk::TextClosestGap
  #    ::tk::TextSelectTo
  #    ::tk::TextPasteSelection
  #    ::tk::TextButton1
  #    ::tk::TextAutoScan


  proc copyBindingClass {class newClass {mapping {}}} {
      # call this proc to make $newClass inherit the bindings of $class, but with some substitutions
      # Derived from https://wiki.tcl-lang.org/2944 by George Peter Staplin
      set bindingList [bind $class]
      foreach binding $bindingList {
          bind $newClass $binding [string map $mapping [bind $class $binding]]
      }
  }

  copyBindingClass Text modernText  {
     tk_textPaste            modernText::modernPaste
     tk::TextSelectTo        modernText::TextSelectTo
     tk::TextPasteSelection  modernText::TextPasteSelection
     tk::TextButton1         modernText::TextButton1
     tk::TextAutoScan        modernText::TextAutoScan
  }


  # Now alter some of the bindings

  # Keyboard bindings to implement "Smart Home/End" and Escape (to clear the selection)
  bind modernText <Home>  {
      tk::TextSetCursor %W  [::modernText::homeIndex %W insert]
  }

  bind modernText <End>  {
      tk::TextSetCursor %W  [::modernText::endIndex %W insert]
  }

  bind modernText <Shift-Home> {
      tk::TextKeySelect %W [::modernText::homeIndex %W insert]
  }

  bind modernText <Shift-End> {
      tk::TextKeySelect %W [::modernText::endIndex %W insert]
  }

  bind modernText <Escape>  {
      %W tag remove sel 0.0 end
  }

  # Mouse bindings: when the modernText bindings are copied from the Text bindings by copyBindingClass (above),
  # they are modified so that they use the modernText functions.  The further modifications below:
  # (1) Use ::modernText::bCount to deal with out-of-order multiple clicks
  # (2) (With Shift modifier only) Use ::modernText::mouseSelectIgnoresKbd and ::modernText::variableAnchor to
  #     change the text selection algorithm.

  bind modernText <1> {
      set ::modernText::bCount 1
      modernText::TextButton1 %W %x %y
      %W tag remove sel 0.0 end
  }

  bind modernText <Double-1> {
      if {$::modernText::bCount != 1} {
          # The previous Button-1 event was not a single-click, but a double, triple, or quadruple.
          # We can simplify the bindings if we ensure that a double-click is *always* preceded by a single-click.
          # So inject a <1> handler before doing <Double-1> ...
          set ::modernText::bCount 1
          modernText::TextButton1 %W %x %y
          %W tag remove sel 0.0 end
          # ... end of copied <1> handler ...
      }
      #     ... now process the <Double-1> event.
      set ::modernText::bCount 2
      set tk::Priv(selectMode) word
      modernText::TextSelectTo %W %x %y
      catch {%W mark set insert sel.first}
  }

  bind modernText <Triple-1> {
      if {$::modernText::bCount != 2} {
          # ignore an out-of-order triple click.  This has no adverse consequences.
          continue
      }
      set ::modernText::bCount 3
      set tk::Priv(selectMode) line
      modernText::TextSelectTo %W %x %y
      catch {%W mark set insert sel.first}
  }

  bind modernText <Quadruple-1> {
      # don't care if a quadruple click is out-of-order (i.e. follows a quadruple click, not a triple click).
      # the binding does nothing except set bCount.
      set ::modernText::bCount 4
  }


  bind modernText <Shift-1> {
      set ::modernText::bCount 1
      if {!$::modernText::mouseSelectIgnoresKbd && [%W tag ranges sel] eq ""} {
          # Move the selection anchor mark to the old insert mark
          # Should the mark's gravity be set?
          %W mark set tk::anchor%W insert
      }

      if {$::modernText::variableAnchor} {
          tk::TextResetAnchor %W @%x,%y
          # if sel exists, sets anchor to end furthest from x,y
          # changes anchor only, not insert
      }

      set tk::Priv(selectMode) char
      modernText::TextSelectTo %W %x %y
  }

  bind modernText <Double-Shift-1>        {
      if {$::modernText::bCount != 1} {
          # The previous Button-1 event was not a single-click, but a double, triple, or quadruple.
          # We can simplify the bindings if we ensure that a double-click is *always* preceded by a single-click.
          # So inject a <Shift-1> handler before doing <Double-Shift-1> ...
          set ::modernText::bCount 1
          if {!$::modernText::mouseSelectIgnoresKbd && [%W tag ranges sel] eq ""} {
              # Move the selection anchor mark to the old insert mark
              # Should the mark's gravity be set?
              %W mark set tk::anchor%W insert
          }

          if {$::modernText::variableAnchor} {
              tk::TextResetAnchor %W @%x,%y
              # if sel exists, sets anchor to end furthest from x,y
              # changes anchor only, not insert
          }

          set tk::Priv(selectMode) char
          modernText::TextSelectTo %W %x %y
          # ... end of copied <Shift-1> handler ...

      }
      #     ... now process the <Double-Shift-1> event.
      set ::modernText::bCount 2
      set tk::Priv(selectMode) word
      modernText::TextSelectTo %W %x %y 1
  }

  bind modernText <Triple-Shift-1>        {
      if {$::modernText::bCount != 2} {
          # ignore an out-of-order triple click.  This has no adverse consequences.
          continue
      }
      set ::modernText::bCount 3
      set tk::Priv(selectMode) line
      modernText::TextSelectTo %W %x %y
  }

  bind modernText <Quadruple-Shift-1> {
      # don't care if a quadruple click is out-of-order (i.e. follows a quadruple click, not a triple click).
      # the binding does nothing except set bCount.
      set ::modernText::bCount 4
  }

  }