#ifndef MODEL_H
#define MODEL_H

#include <math.h>

// --- StandardScaler parameters (replace X,Y,Z,W with your means) ---
static const float SCALER_MEAN[4] = {4.1761066f, 4.1695733f, 0.2533f,
                                     0.306666f};
static const float SCALER_SCALE[4] = {1.943794169990457f, 2.1580158366631346f,
                                      0.4349201714746691f,
                                      0.46110977242108225f};

// --- IsolationForest threshold (offset_ from your model) ---
// Anomaly if score < IF_THRESHOLD
static const float IF_THRESHOLD = -0.6118492784927119;

// Normalize raw features into scaled[4]
inline void scale_input(const float raw[4], float scaled[4]) {
  for (int i = 0; i < 4; i++) {
    scaled[i] = (raw[i] - SCALER_MEAN[i]) / SCALER_SCALE[i];
  }
}

// A simple “anomaly score” function: average abs(scaled[i])
// Returns 1 if anomaly, 0 if normal
inline int model_predict(const float scaled[4]) {
  float score = 0.0f;
  for (int i = 0; i < 4; i++) {
    score += fabsf(scaled[i]);
  }
  score /= 4.0f;
  return (score < IF_THRESHOLD) ? 1 : 0;
}

#endif // MODEL_H

// MEANS = [4.176106666666667, (4.169573333333333), 0.25333333333333335,
// 0.30666666666666664]
// SCALES= [1.943794169990457, 2.1580158366631346,
// 0.4349201714746691, 0.46110977242108225] OFFSET= -0.6118492784927119
