.PHONY: str
str:
	dart lib/l10n/tools/sync_string.dart
	flutter pub get
	flutter pub get