for aname in AUTHOR_*.py; do
	echo "Processing file: $aname"
	python3 $aname > "${aname%.py}_top20_citedby.txt"
done
