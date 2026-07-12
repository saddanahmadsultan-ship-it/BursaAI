"""
=========================================
BursaAI Brain Engine
Version : 3.0 Stable
=========================================

Generate AI Trading Narrative
"""


def ai_summary(item):

    score = item.get("Score", 0)

    confidence = item.get("Confidence", 0)

    strategy = item.get("Signal", "UNKNOWN")

    trend = item.get("Trend", "UNKNOWN")

    volume = item.get("Volume", "UNKNOWN")

    rr = item.get("RR", None)

    summary = []

    # =====================================
    # Trend
    # =====================================

    if "UP" in trend:

        summary.append(
            "Trend keseluruhan berada dalam keadaan bullish."
        )

    elif "DOWN" in trend:

        summary.append(
            "Trend keseluruhan masih bearish."
        )

    else:

        summary.append(
            "Trend berada dalam keadaan sideways."
        )

    # =====================================
    # Volume
    # =====================================

    if volume == "STRONG":

        summary.append(
            "Volume menunjukkan minat belian yang tinggi."
        )

    elif volume == "GOOD":

        summary.append(
            "Volume berada pada tahap yang sihat."
        )

    elif volume == "WEAK":

        summary.append(
            "Volume masih lemah."
        )

    # =====================================
    # Strategy
    # =====================================

    if "STRONG BUY" in strategy:

        summary.append(
            "AI mengesyorkan pembelian yang agresif."
        )

    elif "BUY" in strategy:

        summary.append(
            "Kaunter sesuai dipertimbangkan untuk pembelian."
        )

    elif "WATCH" in strategy:

        summary.append(
            "Teruskan memantau sebelum membuat keputusan."
        )

    elif "HOLD" in strategy:

        summary.append(
            "Pegang posisi sedia ada."
        )

    else:

        summary.append(
            "Risiko masih tinggi untuk membuka posisi."
        )

    # =====================================
    # Confidence
    # =====================================

    if confidence >= 90:

        summary.append(
            "Tahap keyakinan AI sangat tinggi."
        )

    elif confidence >= 80:

        summary.append(
            "Tahap keyakinan AI adalah tinggi."
        )

    elif confidence >= 70:

        summary.append(
            "Tahap keyakinan AI sederhana."
        )

    else:

        summary.append(
            "Tahap keyakinan AI masih rendah."
        )

    # =====================================
    # Score
    # =====================================

    if score >= 90:

        summary.append(
            "Skor keseluruhan amat cemerlang."
        )

    elif score >= 80:

        summary.append(
            "Skor keseluruhan sangat baik."
        )

    elif score >= 70:

        summary.append(
            "Skor keseluruhan memuaskan."
        )

    else:

        summary.append(
            "Skor keseluruhan masih lemah."
        )

    # =====================================
    # Risk Reward
    # =====================================

    if rr is not None:

        if rr >= 3:

            summary.append(
                "Risk Reward sangat menarik."
            )

        elif rr >= 2:

            summary.append(
                "Risk Reward memenuhi syarat."
            )

        else:

            summary.append(
                "Risk Reward kurang menarik."
            )

    # =====================================
    # Final Conclusion
    # =====================================

    if confidence >= 85 and score >= 80 and "BUY" in strategy:

        summary.append(
            "KESIMPULAN: Calon terbaik untuk dipertimbangkan."
        )

    elif confidence >= 70:

        summary.append(
            "KESIMPULAN: Tunggu pengesahan tambahan."
        )

    else:

        summary.append(
            "KESIMPULAN: Tidak disyorkan untuk entry sekarang."
        )

    return "\n".join(summary)