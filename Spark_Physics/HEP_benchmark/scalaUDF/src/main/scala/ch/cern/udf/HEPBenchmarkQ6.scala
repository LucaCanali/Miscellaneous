package ch.cern.udf

//
// This implements Scala UDFs for the HEP benchmark using Apache Spark
// See https://github.com/LucaCanali/Miscellaneous/Spark_Physics
//

import org.apache.spark.sql.api.java.{UDF1, UDF3}
import org.apache.spark.sql.Row
// import scala.math.{abs, cos, cosh, sin, sinh, sqrt}
import net.jafama.FastMath.{abs, cos, cosh, sin, sinh, sqrt} // use faster math libraries

// This is used by Q6 Solution 1 and Solution 2
class array_combinations extends UDF1[Seq[Row], Seq[Seq[Row]]] {
  def call(in: Seq[Row]): Seq[Seq[Row]] = {
    val out = in.combinations(3).toSeq

    out
  }
}

//
// This is used by Q6 Solution 1: Offload all computations to Scala UDF
//

case class LorentzPtEtaPhiM (Pt: Float, Eta: Float, Phi: Float, M: Float)

case class LorentzPxPyPzE (Px: Float, Py: Float, Pz: Float, E: Float)

case class JetPtBtag(pt: Float, Btag: Float)

class triJetSelectedPtBtag extends UDF1[Seq[Row], JetPtBtag] {
  def call (jList: Seq[Row]): JetPtBtag = {
    val allCombinations = jList.combinations(3).toList
    val triJetMasses = for (j <- allCombinations) yield(abs(invariantMassPtEtaPhiM(j) - 172.5f))
    val indexTriJet = triJetMasses.zipWithIndex.min._2
    val selectedTriJet = allCombinations(indexTriJet)

    val pt = PtSum(selectedTriJet)
    val maxBtag = computeMaxBtag(selectedTriJet)

    JetPtBtag(pt, maxBtag)
  }

  def invariantMassPtEtaPhiM(particlesPtEtaPhiM: Seq[Row]): Float = {

    val particlesPxPyPzE = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        PtEtaPhiM2PxPyPzE(LorentzPtEtaPhiM(pt, eta, phi, m))
    }

    val sumMomenta = particlesPxPyPzE.reduce(add)
    val mass = sqrt(sumMomenta.E * sumMomenta.E - sumMomenta.Px * sumMomenta.Px - sumMomenta.Py * sumMomenta.Py - sumMomenta.Pz * sumMomenta.Pz).toFloat
    mass
  }

  def PtSum(particlesPtEtaPhiM: Seq[Row]): Float = {

    val particlesPxPyPzE = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        PtEtaPhiM2PxPyPzE(LorentzPtEtaPhiM(pt, eta, phi, m))
    }

    val sumMomenta = particlesPxPyPzE.reduce(add)
    val pt = sqrt(sumMomenta.Px * sumMomenta.Px + sumMomenta.Py * sumMomenta.Py).toFloat
    pt
  }

  def computeMaxBtag(particlesPtEtaPhiM: Seq[Row]): Float = {
    val Btag = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        btag
    }
    Btag.max
  }

  def add(p1: LorentzPxPyPzE, p2: LorentzPxPyPzE): LorentzPxPyPzE = {
    LorentzPxPyPzE(p1.Px + p2.Px, p1.Py + p2.Py, p1.Pz + p2.Pz, p1.E + p2.E)
  }

  def PtEtaPhiM2PxPyPzE(in: LorentzPtEtaPhiM): LorentzPxPyPzE = {
    val out = LorentzPxPyPzE(
      in.Pt * cos(in.Phi).toFloat,
      in.Pt * sin(in.Phi).toFloat,
      in.Pt * sinh(in.Eta).toFloat,
      sqrt((in.Pt * cosh(in.Eta)*(in.Pt * cosh(in.Eta)) + in.M * in.M)).toFloat
    )
    out
  }
}


//
// This is used by Q6 Solution 2: Compute 3-jet combinations and TriJet mass in Scala UDF
//

case class JetMassPtBtag(mass: Float, pt: Float, btag: Float)

class triJetPtMassDeltaBtag extends UDF1[Seq[Row], JetMassPtBtag] {
  def call(jets: Seq[Row]): JetMassPtBtag = {

    val triJetMassPtBtag = invariantMassPtEtaPhiM(jets)

    JetMassPtBtag(abs(triJetMassPtBtag.mass -172.5f), triJetMassPtBtag.pt, triJetMassPtBtag.btag)

  }

  def invariantMassPtEtaPhiM(particlesPtEtaPhiM: Seq[Row]): JetMassPtBtag = {

    val particlesPxPyPzE = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        PtEtaPhiM2PxPyPzE(LorentzPtEtaPhiM(pt, eta, phi, m))
    }

    val sumMomenta = particlesPxPyPzE.reduce(add)
    val mass = sqrt(sumMomenta.E * sumMomenta.E - sumMomenta.Px * sumMomenta.Px - sumMomenta.Py * sumMomenta.Py - sumMomenta.Pz * sumMomenta.Pz).toFloat
    val pt = sqrt(sumMomenta.Px * sumMomenta.Px + sumMomenta.Py * sumMomenta.Py).toFloat

    val maxBtag = computeMaxBtag(particlesPtEtaPhiM)

    JetMassPtBtag(mass, pt, maxBtag)
  }

  def computeMaxBtag(particlesPtEtaPhiM: Seq[Row]): Float = {
    val Btag = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        btag
    }
    Btag.max
  }

  def add(p1: LorentzPxPyPzE, p2: LorentzPxPyPzE): LorentzPxPyPzE = {
    LorentzPxPyPzE(p1.Px + p2.Px, p1.Py + p2.Py, p1.Pz + p2.Pz, p1.E + p2.E)
  }

  def PtEtaPhiM2PxPyPzE(in: LorentzPtEtaPhiM): LorentzPxPyPzE = {
    val out = LorentzPxPyPzE(
      in.Pt * cos(in.Phi).toFloat,
      in.Pt * sin(in.Phi).toFloat,
      in.Pt * sinh(in.Eta).toFloat,
      sqrt((in.Pt * cosh(in.Eta) * (in.Pt * cosh(in.Eta)) + in.M * in.M)).toFloat
    )
    out
  }
}

//
// This is used by Q6 Solution 3: Only TriJet mass in Scala UDF
//

class triJetPtMassBtag extends UDF3[Row, Row, Row, JetMassPtBtag] {
  def call(j1: Row, j2: Row, j3: Row): JetMassPtBtag = {

    val jets = Seq(j1, j2, j3)
    val triJetMassPtBtag = invariantMassPtEtaPhiM(jets)

    JetMassPtBtag(triJetMassPtBtag.mass, triJetMassPtBtag.pt, triJetMassPtBtag.btag)
  }

  def invariantMassPtEtaPhiM(particlesPtEtaPhiM: Seq[Row]): JetMassPtBtag = {

    val particlesPxPyPzE = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        PtEtaPhiM2PxPyPzE(LorentzPtEtaPhiM(pt, eta, phi, m))
    }

    val sumMomenta = particlesPxPyPzE.reduce(add)
    val mass = sqrt(sumMomenta.E * sumMomenta.E - sumMomenta.Px * sumMomenta.Px - sumMomenta.Py * sumMomenta.Py - sumMomenta.Pz * sumMomenta.Pz).toFloat
    val pt = sqrt(sumMomenta.Px * sumMomenta.Px + sumMomenta.Py * sumMomenta.Py).toFloat

    val maxBtag = computeMaxBtag(particlesPtEtaPhiM)
    JetMassPtBtag(mass, pt, maxBtag)
  }

  def computeMaxBtag(particlesPtEtaPhiM: Seq[Row]): Float = {
    val Btag = particlesPtEtaPhiM map {
      case Row(pt: Float, eta: Float, phi: Float, m: Float, btag: Float) =>
        btag
    }
    Btag.max
  }

  def add(p1: LorentzPxPyPzE, p2: LorentzPxPyPzE): LorentzPxPyPzE = {
    LorentzPxPyPzE(p1.Px + p2.Px, p1.Py + p2.Py, p1.Pz + p2.Pz, p1.E + p2.E)
  }

  def PtEtaPhiM2PxPyPzE(in: LorentzPtEtaPhiM): LorentzPxPyPzE = {
    val out = LorentzPxPyPzE(
      in.Pt * cos(in.Phi).toFloat,
      in.Pt * sin(in.Phi).toFloat,
      in.Pt * sinh(in.Eta).toFloat,
      sqrt((in.Pt * cosh(in.Eta) * (in.Pt * cosh(in.Eta)) + in.M * in.M)).toFloat
    )
    out
  }
}
