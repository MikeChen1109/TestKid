// Copyright 2019 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

import 'dart:async';
import 'package:firebase_crashlytics/firebase_crashlytics.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'TestApp.dart';

//ignore: avoid_void_async
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // FirebaseAppManager().runAppWithRecordingError(MainPage());
  runZonedGuarded(() {
    SystemChrome.setPreferredOrientations(
      [
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
      ],
    ).then((_) {
      runApp(const ProviderScope(child: TestAppHome()));
    });
  }, FirebaseCrashlytics.instance.recordError);
}
