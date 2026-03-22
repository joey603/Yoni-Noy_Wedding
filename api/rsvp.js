const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID;
const AIRTABLE_TOKEN = process.env.AIRTABLE_TOKEN;
const AIRTABLE_TABLE_NAME = process.env.AIRTABLE_TABLE_NAME || "RSVP";

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  if (!AIRTABLE_BASE_ID || !AIRTABLE_TOKEN) {
    return res.status(500).json({ error: "Missing Airtable environment variables" });
  }

  try {
    const { lastName, firstName, houppa, guests, message } = req.body || {};

    if (!lastName || !firstName || !houppa) {
      return res.status(400).json({ error: "Missing required RSVP fields" });
    }

    const response = await fetch(
      `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${encodeURIComponent(AIRTABLE_TABLE_NAME)}`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${AIRTABLE_TOKEN}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          records: [
            {
              fields: {
                Nom: String(lastName).trim(),
                Prenom: String(firstName).trim(),
                "Presence houppa": String(houppa).trim(),
                "Nombre de personnes": Number.isFinite(Number(guests)) ? Number(guests) : 1,
                Message: String(message || "").trim(),
              },
            },
          ],
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        error: data?.error?.message || "Airtable request failed",
      });
    }

    return res.status(200).json({ ok: true, record: data.records?.[0] || null });
  } catch (error) {
    return res.status(500).json({ error: "Unexpected server error" });
  }
};
