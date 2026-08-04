"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PerfumeSearchInput } from "@/components/PerfumeSearchInput";
import { PerfumeImage } from "@/components/PerfumeImage";
import { LayeringResults } from "@/components/LayeringResults";
import { LayeringHistoryEntry } from "@/components/LayeringHistoryEntry";
import { Loader } from "@/components/ui/loader";
import { proposerLayering } from "@/lib/api";
import {
  obtenirLayeringsSauvegardes,
  sauvegarderLayering,
  supprimerLayering,
} from "@/lib/layeringStorage";

/**
 * Page dédiée au layering autonome : le client recherche un parfum qu'il
 * possède déjà, on appelle le moteur de layering (POST /api/layering) et
 * on affiche le résultat en pleine page (pas en volet, contrairement à
 * LayeringPanel utilisé depuis le chat). Chaque layering généré est
 * sauvegardé en localStorage, consultable depuis "Mes layerings" sans
 * relancer d'appel API.
 */
export default function PageLayering() {
  const [chargement, setChargement] = useState(false);
  const [erreur, setErreur] = useState(null);
  const [resultatActuel, setResultatActuel] = useState(null); // { parfum_reference, perfumes, reply }
  const [historique, setHistorique] = useState([]);

  // localStorage n'existe que côté navigateur : chargé une fois au montage.
  useEffect(() => {
    setHistorique(obtenirLayeringsSauvegardes());
  }, []);

  const lancerLayering = async (parfum) => {
    setErreur(null);
    setResultatActuel(null);
    setChargement(true);

    try {
      const reponse = await proposerLayering(parfum.id);
      setResultatActuel(reponse);

      const listeMiseAJour = sauvegarderLayering({
        parfumDeBase: {
          id: parfum.id,
          nom: reponse.parfum_reference.nom,
          marque: reponse.parfum_reference.marque,
          image_url: reponse.parfum_reference.image_url,
        },
        propositions: reponse.perfumes,
        guide: reponse.reply,
      });
      setHistorique(listeMiseAJour);
    } catch (erreurAppel) {
      setErreur(erreurAppel.message || "Une erreur est survenue. Merci de réessayer.");
    } finally {
      setChargement(false);
    }
  };

  // Réaffiche une entrée déjà sauvegardée : aucune requête API, tout est
  // déjà dans l'enregistrement localStorage.
  const afficherEntreeHistorique = (entree) => {
    setErreur(null);
    setResultatActuel({
      parfum_reference: entree.parfum_de_base,
      perfumes: entree.propositions,
      reply: entree.guide,
    });
  };

  const supprimerEntree = (id) => {
    setHistorique(supprimerLayering(id));
  };

  return (
    <div className="flex min-h-screen flex-col bg-nayaar-cream">
      <Header
        nav={
          <Link
            href="/"
            className="label-caps flex items-center gap-1.5 text-nayaar-ink/70 transition-colors hover:text-nayaar-gold"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Chat
          </Link>
        }
      />

      <main className="flex-1">
        <div className="mx-auto flex w-full max-w-2xl flex-col gap-10 px-4 py-10">
          <div className="text-center">
            <h2 className="font-serif text-2xl text-nayaar-ink">
              Layering personnalisé
            </h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-nayaar-ink/70">
              Indiquez un parfum que vous possédez déjà : nous vous proposons
              comment le sublimer en superposition, avec l&apos;ordre
              d&apos;application et les conseils d&apos;usage.
            </p>
          </div>

          <PerfumeSearchInput onSelect={lancerLayering} />

          {chargement && (
            <div className="flex justify-center py-8">
              <Loader variant="typing" size="md" />
            </div>
          )}

          {erreur && !chargement && (
            <p className="text-center text-sm italic text-nayaar-ink/70">
              {erreur}
            </p>
          )}

          {resultatActuel && !chargement && !erreur && (
            <section className="flex flex-col gap-4">
              {/* Rappel du parfum de base */}
              <div className="flex items-center gap-3 rounded-xl border border-nayaar-gold-soft/50 bg-white p-3 shadow-sm">
                <PerfumeImage
                  src={resultatActuel.parfum_reference.image_url}
                  nom={resultatActuel.parfum_reference.nom}
                  className="h-14 w-14 shrink-0 rounded-lg"
                  sizes="56px"
                />
                <div className="min-w-0">
                  <p className="label-caps text-nayaar-gold">
                    {resultatActuel.parfum_reference.marque}
                  </p>
                  <p className="truncate font-serif text-base text-nayaar-ink">
                    {resultatActuel.parfum_reference.nom}
                  </p>
                </div>
              </div>

              <LayeringResults
                perfumes={resultatActuel.perfumes}
                reply={resultatActuel.reply}
              />
            </section>
          )}

          {/* Historique — toujours visible, même sans résultat affiché */}
          <section className="flex flex-col gap-3 border-t border-nayaar-gold-soft/40 pt-6">
            <h3 className="label-caps">Mes layerings</h3>

            {historique.length === 0 ? (
              <p className="text-sm text-nayaar-ink/60">
                Aucun layering sauvegardé pour l&apos;instant — vos recherches
                apparaîtront ici.
              </p>
            ) : (
              <ul className="flex flex-col gap-2">
                {historique.map((entree) => (
                  <LayeringHistoryEntry
                    key={entree.id}
                    entree={entree}
                    onSelect={() => afficherEntreeHistorique(entree)}
                    onDelete={() => supprimerEntree(entree.id)}
                  />
                ))}
              </ul>
            )}
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
