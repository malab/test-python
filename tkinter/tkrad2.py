#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkRAD

mainwindow = tkRAD.RADXMLMainWindow()

xml_main = """
    <tkwidget>
        <!-- you can mix as if you like -->
        <ttkstyle
            apply="myButton.TButton"
            background="darkgreen"
            foreground="white"
        >
        <![CDATA[
            /*
                now you can use CSS-like syntax for
                all of your ttk widget style
                definitions;
            */

            /*
                notice: the '*' element means 'apply to ALL elements';
            */

            * {
                background: #ffffdd;
                foreground: chocolate;
            }

            /** Doxygen comments */

            /*! Doxygen comments */

            /*
                element:pseudo-format
                matches with any ttk widget state
                e.g.
                :active         :!active
                :background     :!background
                :disabled       :!disabled
                :focus          :!focus
                :invalid        :!invalid
                :pressed        :!pressed
                :readonly       :!readonly
                :selected       :!selected
            */

            *:focus {
                background: yellow; /* only when focused */
            }

            /*
                pseudo-formats:
                you may use any combination you like
                even with '!state' (not-state logic)
            */

            TButton:active:!pressed {

                background: orange; /*  when hovered,
                                        but don't press
                                        oranges!
                                    */
            }

            newName.TCheckbutton {}

            /***********************************************************
                you can put comments
                anywhere you like
            ***********************************************************/

            Treeview
                :selected
                :focus
                :!disabled
            {
                font: "URW Palladio L" 16 italic bold;
            }

            TLabel :focus {
                padding: 5mm;
            }

            TRadiobutton :selected {
                indicatorcolor: orange;
            }

            newName.TLabel,
            TLabel:!disabled,
            /* this one is the most important one! */
            TRadiobutton
                :focus      /* applies only for TRadiobutton */
                :!pressed   /* not for the previous ones */
            {
                font: sans 12;
                indicatorcolor: blue;
            }
        ]]>
        </ttkstyle>
        <!-- the following style is for Tkinter NATIVE widgets -->
        <style
            id="style1"
            font="'URW Palladio L' 16 italic bold"
            bg="red"
            fg="white"
        />
        <label
            text="Hello good people!"
            bg="maroon"
            style="style1"
            layout="pack"
            resizable="width"
        />
        <ttkcheckbutton
            text="Check this out!"
            checked="checked"
            layout="pack"
            resizable="width"
        />
        <ttkcombobox
            values="'hello', 'good', 'people', 123, 456, 789"
            layout="pack"
            resizable="width"
        />
        <ttkmenubutton
            text="Click to show off menu"
            layout="pack"
            resizable="width"
        >
            <tkmenu>
                <menu label="_File">
                    <command label="_Quit" command="@quit" />
                </menu>
            </tkmenu>
        </ttkmenubutton>
        <ttklabel
            text="Please, choose your favourite meal:"
            layout="pack"
            resizable="width"
        />
        <ttklabelframe
            text="Choose"
            layout="pack"
            resizable="yes"
        >
            <ttkradiobutton
                text="Pizza!"
                variable="optgroup1"
                value="pizza"
                layout="pack"
                resizable="yes"
            />
            <ttkradiobutton
                text="Hot-dog!"
                variable="optgroup1"
                value="hotdog"
                selected="selected"
                layout="pack"
                resizable="yes"
            />
            <ttkradiobutton
                text="Hamburger!"
                variable="optgroup1"
                value="hamburger"
                layout="pack"
                resizable="yes"
            />
        </ttklabelframe>
        <ttkbutton
            text="Quit"
            style="myButton.TButton"
            command="@quit"
            layout="pack"
        />
    </tkwidget>
"""

mainwindow.xml_build(xml_main)

mainwindow.run()
