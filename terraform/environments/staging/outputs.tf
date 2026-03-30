output "staging_cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "staging_rds_endpoint" {
  value = module.rds.db_host
}
