#!/bin/sh

df -kT | awk 'BEGIN { print "<openbox_pipe_menu>"; 
		itemFmt="<item label=\"%s: %s\"><action name=\"Execute\"><command>true</command></action></item>\n";
		itemFmt2="<item label=\"%s: %dKB\"><action name=\"Execute\"><command>true</command></action></item>\n";
		menuFmt="<menu id=\"fs_menu_%s\" label=\"%7.2fGB %s\">\n";
		menuNum=0;
		}
	$0 ~ "dev" { 
		menuNum = menuNum + 1;
		printf(menuFmt, menuNum, $5 / 1048576, $7);
		printf(itemFmt, "Filesystem", $1);
		printf(itemFmt, "Type", $2);
		printf(itemFmt2, "Size", $3/1024);
		printf(itemFmt2, "Used", $4/1024);
		printf(itemFmt2, "Avail", $5/1024);
		printf(itemFmt, "Use%", $6);
		printf(itemFmt, "Mounted on", $7);
		print "</menu>";
	}
	END { print "</openbox_pipe_menu>" }
	'
